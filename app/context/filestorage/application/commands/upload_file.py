from __future__ import annotations

import uuid

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.application.ports.file_storage.file_storage_port import FileStoragePort
from app.shared.domain.value_objects.id_vo import Id

from app.context.filestorage.application.dto.file_dto import FileDTO
from app.context.filestorage.application.dto.mappers import file_to_dto
from app.context.filestorage.application.ports.integration.inboard.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.filestorage.domain.aggregates.file import File
from app.context.filestorage.domain.exceptions.file_exceptions import (
    FileTooLargeException,
    FileTypeNotAllowedException,
)
from app.context.filestorage.domain.exceptions.folder_exceptions import (
    FolderNotFoundException,
)
from app.context.filestorage.domain.exceptions.storage_exceptions import (
    StorageNotFoundException,
)
from app.context.filestorage.domain.repositories.file_repository import FileRepository
from app.context.filestorage.domain.repositories.folder_repository import FolderRepository
from app.context.filestorage.domain.repositories.storage_repository import StorageRepository
from app.context.filestorage.domain.value_objects.file_size import FileSize
from app.context.filestorage.domain.value_objects.file_type import FileType
from app.context.filestorage.domain.value_objects.storage_owner_type import StorageOwnerType


_MIME_TO_FILE_TYPE: dict[str, FileType] = {
    "image/": FileType.IMAGE,
    "video/": FileType.VIDEO,
    "audio/": FileType.AUDIO,
    "application/pdf": FileType.PDF,
    "application/zip": FileType.ARCHIVE,
    "application/x-rar-compressed": FileType.ARCHIVE,
    "application/x-tar": FileType.ARCHIVE,
    "application/x-7z-compressed": FileType.ARCHIVE,
    "application/gzip": FileType.ARCHIVE,
    "application/vnd.ms-excel": FileType.SPREADSHEET,
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": FileType.SPREADSHEET,
    "application/vnd.ms-powerpoint": FileType.PRESENTATION,
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": FileType.PRESENTATION,
    "application/msword": FileType.OFFICE,
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": FileType.OFFICE,
    "text/": FileType.CODE,
    "font/": FileType.FONT,
    "application/font-": FileType.FONT,
}


def _detect_file_type(mime_type: str) -> FileType:
    """Определить FileType по MIME-типу."""
    mt = (mime_type or "").lower()
    for prefix, ftype in _MIME_TO_FILE_TYPE.items():
        if mt == prefix or mt.startswith(prefix):
            return ftype
    return FileType.OTHER


class UploadFileCommand(BaseCommand):
    """
    Команда загрузки файла в FileStorage BC.

    Атрибуты:
        caller_id: ID пользователя, выполняющего операцию.
        workspace_id: ID workspace.
        filename: Оригинальное имя файла.
        content_type: MIME-тип.
        file_data: Содержимое файла.
        folder_id: ID папки (None — корень workspace).
        description: Описание.
    """

    caller_id: str
    workspace_id: str
    filename: str
    content_type: str
    file_data: bytes
    folder_id: str | None = None
    description: str | None = None

    model_config = {"arbitrary_types_allowed": True, "frozen": True}


class UploadFileHandler(BaseCommandHandler[UploadFileCommand, FileDTO]):
    """
    Обработчик загрузки файла.

    Проверяет разрешение `files.write`, валидирует размер и тип файла
    относительно квот хранилища, загружает данные в blob-хранилище
    через FileStoragePort, создаёт агрегат File и сохраняет в БД.
    """

    REQUIRED_PERMISSION = "files.write"

    def __init__(
        self,
        file_repo: FileRepository,
        folder_repo: FolderRepository,
        storage_repo: StorageRepository,
        permission_checker: WorkspacePermissionCheckerPort,
        file_storage: FileStoragePort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._file_repo = file_repo
        self._folder_repo = folder_repo
        self._storage_repo = storage_repo
        self._permission_checker = permission_checker
        self._file_storage = file_storage
        self._event_bus = event_bus

    async def handle(self, command: UploadFileCommand) -> FileDTO:
        await self._permission_checker.require_permission(
            user_id=command.caller_id,
            workspace_id=command.workspace_id,
            permission=self.REQUIRED_PERMISSION,
        )

        workspace_id = Id.from_string(command.workspace_id)
        uploader_id = Id.from_string(command.caller_id)

        storage = await self._storage_repo.get_by_owner(
            owner_type=StorageOwnerType.WORKSPACE, owner_id=workspace_id
        )
        if storage is None:
            raise StorageNotFoundException(id=command.workspace_id)

        # Папка (опционально)
        folder_id: Id | None = None
        if command.folder_id:
            folder_id = Id.from_string(command.folder_id)
            folder = await self._folder_repo.get_by_id(folder_id)
            if folder is None:
                raise FolderNotFoundException(id=command.folder_id)
            if folder.workspace_id != workspace_id:
                raise FolderNotFoundException(id=command.folder_id)

        size_bytes = len(command.file_data)
        file_type = _detect_file_type(command.content_type)

        # Лимит на размер одного файла
        if storage.max_file_size_bytes is not None and size_bytes > storage.max_file_size_bytes:
            raise FileTooLargeException(
                max_size=storage.max_file_size_bytes, actual_size=size_bytes
            )
        # Разрешённые типы
        if storage.allowed_file_types is not None and file_type not in storage.allowed_file_types:
            raise FileTypeNotAllowedException(file_type=file_type.value)

        # Резервируем квоту (бросает StorageQuotaExceededException при превышении)
        storage.add_usage(size_bytes)

        # Загрузка в blob-хранилище
        storage_key = f"workspaces/{command.workspace_id}/{uuid.uuid4().hex}/{command.filename}"
        await self._file_storage.upload(
            key=storage_key,
            data=command.file_data,
            content_type=command.content_type,
        )

        # Создание агрегата
        file = File.create(
            name=command.filename,
            original_name=command.filename,
            file_type=file_type,
            size=FileSize(value=size_bytes),
            mime_type=command.content_type,
            storage_id=storage.id,
            storage_path=storage_key,
            uploader_id=uploader_id,
            workspace_id=workspace_id,
            folder_id=folder_id,
        )
        if command.description:
            file.update_description(command.description)

        await self._file_repo.add(file)
        await self._storage_repo.update(storage)

        await self._event_bus.publish_all(file.clear_domain_events())
        await self._event_bus.publish_all(storage.clear_domain_events())

        return file_to_dto(file)

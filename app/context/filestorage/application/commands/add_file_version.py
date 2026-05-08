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
from app.context.filestorage.domain.exceptions.file_exceptions import (
    FileNotFoundException,
    FileTooLargeException,
)
from app.context.filestorage.domain.exceptions.storage_exceptions import (
    StorageNotFoundException,
)
from app.context.filestorage.domain.repositories.file_repository import FileRepository
from app.context.filestorage.domain.repositories.storage_repository import StorageRepository


class AddFileVersionCommand(BaseCommand):
    """
    Команда добавления новой версии файла.

    Атрибуты:
        caller_id: ID пользователя.
        file_id: ID файла.
        file_data: Содержимое новой версии.
        content_type: MIME-тип.
        change_summary: Описание изменений.
    """

    caller_id: str
    file_id: str
    file_data: bytes
    content_type: str
    change_summary: str | None = None

    model_config = {"arbitrary_types_allowed": True, "frozen": True}


class AddFileVersionHandler(BaseCommandHandler[AddFileVersionCommand, FileDTO]):
    """Добавление новой версии файла."""

    REQUIRED_PERMISSION = "files.write"

    def __init__(
        self,
        file_repo: FileRepository,
        storage_repo: StorageRepository,
        permission_checker: WorkspacePermissionCheckerPort,
        file_storage: FileStoragePort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._file_repo = file_repo
        self._storage_repo = storage_repo
        self._permission_checker = permission_checker
        self._file_storage = file_storage
        self._event_bus = event_bus

    async def handle(self, command: AddFileVersionCommand) -> FileDTO:
        file = await self._file_repo.get_by_id(Id.from_string(command.file_id))
        if file is None:
            raise FileNotFoundException(id=command.file_id)
        await self._permission_checker.require_permission(
            user_id=command.caller_id,
            workspace_id=str(file.workspace_id),
            permission=self.REQUIRED_PERMISSION,
        )

        storage = await self._storage_repo.get_by_id(file.storage_id)
        if storage is None:
            raise StorageNotFoundException(id=str(file.storage_id))

        size_bytes = len(command.file_data)
        if storage.max_file_size_bytes is not None and size_bytes > storage.max_file_size_bytes:
            raise FileTooLargeException(
                max_size=storage.max_file_size_bytes, actual_size=size_bytes
            )

        # Учёт квоты: разница новой и прошлой версии
        delta = size_bytes - file.size.value
        if delta > 0:
            storage.add_usage(delta)
        elif delta < 0:
            storage.remove_usage(-delta)

        # Загрузка blob
        storage_key = (
            f"workspaces/{file.workspace_id}/{uuid.uuid4().hex}/{file.original_name}"
        )
        await self._file_storage.upload(
            key=storage_key,
            data=command.file_data,
            content_type=command.content_type,
        )

        file.add_version(
            storage_path=storage_key,
            size_bytes=size_bytes,
            uploader_id=Id.from_string(command.caller_id),
            change_summary=command.change_summary,
        )
        await self._file_repo.update(file)
        await self._storage_repo.update(storage)

        await self._event_bus.publish_all(file.clear_domain_events())
        await self._event_bus.publish_all(storage.clear_domain_events())
        return file_to_dto(file)

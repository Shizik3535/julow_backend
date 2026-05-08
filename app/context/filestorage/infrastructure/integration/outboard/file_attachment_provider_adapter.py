from __future__ import annotations

import uuid

from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.application.ports.file_storage.file_storage_port import FileStoragePort
from app.shared.domain.value_objects.id_vo import Id

from app.context.filestorage.application.commands.upload_file import _detect_file_type
from app.context.filestorage.application.ports.integration.outboard.file_attachment_provider import (
    AttachmentUploadResult,
    FileAttachmentProvider,
)
from app.context.filestorage.domain.aggregates.file import File
from app.context.filestorage.domain.exceptions.file_exceptions import (
    FileTooLargeException,
    FileTypeNotAllowedException,
)
from app.context.filestorage.domain.exceptions.storage_exceptions import (
    StorageNotFoundException,
)
from app.context.filestorage.domain.repositories.file_repository import FileRepository
from app.context.filestorage.domain.repositories.storage_repository import StorageRepository
from app.context.filestorage.domain.value_objects.file_size import FileSize
from app.context.filestorage.domain.value_objects.file_status import FileStatus
from app.context.filestorage.domain.value_objects.storage_owner_type import StorageOwnerType


class FileAttachmentProviderAdapter(FileAttachmentProvider):
    """
    Реализация FileAttachmentProvider.

    Регистрирует файл-вложение как полноценный агрегат ``File``
    в FileStorage BC, учитывает квоту, эмитит доменные события.

    Использует те же примитивы, что и ``UploadFileHandler``, но без
    проверки RBAC ``files.write`` — авторизация остаётся на стороне
    consuming BC (например, ``tasks.update_own`` или авторство комментария).
    """

    def __init__(
        self,
        file_repo: FileRepository,
        storage_repo: StorageRepository,
        file_storage: FileStoragePort,
        event_bus: DomainEventBus,
    ) -> None:
        self._file_repo = file_repo
        self._storage_repo = storage_repo
        self._file_storage = file_storage
        self._event_bus = event_bus

    async def upload_attachment(
        self,
        *,
        workspace_id: str,
        uploader_id: str,
        filename: str,
        file_data: bytes,
        content_type: str,
        folder_id: str | None = None,
    ) -> AttachmentUploadResult:
        ws_id = Id.from_string(workspace_id)
        uploader = Id.from_string(uploader_id)

        storage = await self._storage_repo.get_by_owner(
            owner_type=StorageOwnerType.WORKSPACE, owner_id=ws_id
        )
        if storage is None:
            raise StorageNotFoundException(id=workspace_id)

        size_bytes = len(file_data)
        file_type = _detect_file_type(content_type)

        if (
            storage.max_file_size_bytes is not None
            and size_bytes > storage.max_file_size_bytes
        ):
            raise FileTooLargeException(
                max_size=storage.max_file_size_bytes, actual_size=size_bytes
            )
        if (
            storage.allowed_file_types is not None
            and file_type not in storage.allowed_file_types
        ):
            raise FileTypeNotAllowedException(file_type=file_type.value)

        # Резервируем квоту (бросает StorageQuotaExceededException при превышении)
        storage.add_usage(size_bytes)

        storage_key = (
            f"workspaces/{workspace_id}/attachments/{uuid.uuid4().hex}/{filename}"
        )
        await self._file_storage.upload(
            key=storage_key,
            data=file_data,
            content_type=content_type,
        )

        file = File.create(
            name=filename,
            original_name=filename,
            file_type=file_type,
            size=FileSize(value=size_bytes),
            mime_type=content_type,
            storage_id=storage.id,
            storage_path=storage_key,
            uploader_id=uploader,
            workspace_id=ws_id,
            folder_id=Id.from_string(folder_id) if folder_id else None,
        )

        await self._file_repo.add(file)
        await self._storage_repo.update(storage)
        await self._event_bus.publish_all(file.clear_domain_events())
        await self._event_bus.publish_all(storage.clear_domain_events())

        url = await self._file_storage.get_url(key=storage_key, expires_in=None)
        return AttachmentUploadResult(
            file_id=str(file.id),
            url=url,
            storage_path=storage_key,
            size_bytes=size_bytes,
        )

    async def delete_attachment(self, file_id: str) -> None:
        try:
            file_uuid = Id.from_string(file_id)
        except (ValueError, TypeError):
            # Невалидный UUID — идемпотентно игнорируем.
            return
        file = await self._file_repo.get_by_id(file_uuid)
        if file is None:
            return

        storage = await self._storage_repo.get_by_id(file.storage_id)
        if storage is not None:
            storage.remove_usage(file.size.value)

        # Удаление blob — best-effort: даже если S3 недоступен, мы должны
        # пометить агрегат как удалённый, чтобы освободить квоту в БД.
        try:
            await self._file_storage.delete(file.storage_path)
        except Exception:  # noqa: BLE001
            pass

        # Помечаем как удалённый и публикуем события ДО физического удаления
        # из БД, чтобы при сбое publish'а транзакция откатилась и квота не
        # ушла в рассинхрон с реальным состоянием.
        if file.status != FileStatus.DELETED:
            file.delete_permanently()
        await self._file_repo.update(file)
        if storage is not None:
            await self._storage_repo.update(storage)
        await self._event_bus.publish_all(file.clear_domain_events())
        if storage is not None:
            await self._event_bus.publish_all(storage.clear_domain_events())
        await self._file_repo.delete(file.id)

    async def get_attachment_url(
        self, file_id: str, expires_in: int | None = 3600
    ) -> str | None:
        try:
            file_uuid = Id.from_string(file_id)
        except (ValueError, TypeError):
            return None
        file = await self._file_repo.get_by_id(file_uuid)
        if file is None:
            return None
        return await self._file_storage.get_url(
            key=file.storage_path, expires_in=expires_in
        )

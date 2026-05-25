from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.application.ports.file_storage.file_storage_port import FileStoragePort
from app.shared.domain.exceptions import BusinessRuleViolationException
from app.shared.domain.value_objects.id_vo import Id

from app.context.filestorage.application.ports.integration.inboard.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.filestorage.domain.events.file_events import FileDownloaded
from app.context.filestorage.domain.exceptions.file_exceptions import (
    FileNotFoundException,
    FileTrashedException,
    VirusDetectedException,
)
from app.context.filestorage.domain.repositories.file_repository import FileRepository
from app.context.filestorage.domain.value_objects.file_status import FileStatus
from app.context.filestorage.domain.value_objects.virus_scan_status import VirusScanStatus


class GetFileDownloadUrlQuery(BaseQuery):
    """Запрос получения presigned URL для скачивания файла."""

    file_id: str
    caller_id: str
    expires_in: int = 3600


class GetFileDownloadUrlHandler(BaseQueryHandler[GetFileDownloadUrlQuery, dict]):
    """
    Получение presigned URL для скачивания файла.

    Эмитит событие `FileDownloaded` (через event_bus).

    Скачивание блокируется, если:
    - файл в корзине / удалён → ``FileTrashedException``;
    - файл заражён → ``VirusDetectedException``;
    - файл ещё не просканирован (``PENDING``) и
      ``block_pending_downloads=True`` → ``BusinessRuleViolationException``.
    """

    REQUIRED_PERMISSION = "files.read"

    def __init__(
        self,
        file_repo: FileRepository,
        permission_checker: WorkspacePermissionCheckerPort,
        file_storage: FileStoragePort,
        event_bus: DomainEventBus,
        block_pending_downloads: bool = True,
    ) -> None:
        super().__init__()
        self._file_repo = file_repo
        self._permission_checker = permission_checker
        self._file_storage = file_storage
        self._event_bus = event_bus
        self._block_pending = block_pending_downloads

    async def handle(self, query: GetFileDownloadUrlQuery) -> dict:
        file = await self._file_repo.get_by_id(Id.from_string(query.file_id))
        if file is None:
            raise FileNotFoundException(id=query.file_id)
        if file.status == FileStatus.TRASHED or file.status == FileStatus.DELETED:
            raise FileTrashedException()
        if file.scan_status == VirusScanStatus.INFECTED:
            raise VirusDetectedException()
        if (
            self._block_pending
            and file.scan_status == VirusScanStatus.PENDING
        ):
            raise BusinessRuleViolationException(
                rule="VirusScanCompleted",
                message="Файл ещё не просканирован антивирусом",
            )
        await self._permission_checker.require_permission(
            user_id=query.caller_id,
            workspace_id=str(file.workspace_id),
            permission=self.REQUIRED_PERMISSION,
        )
        url = await self._file_storage.get_url(
            key=file.storage_path, expires_in=query.expires_in
        )
        await self._event_bus.publish_all(
            [FileDownloaded(file_id=str(file.id), downloader_id=query.caller_id)]
        )
        return {
            "url": url,
            "expires_in": query.expires_in,
            "file_id": str(file.id),
            "name": file.name,
            "mime_type": file.mime_type,
            "size_bytes": file.size.value,
        }

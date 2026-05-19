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


class GetFileContentQuery(BaseQuery):
    """Запрос получения сырого содержимого файла (bytes) с метаданными.

    В отличие от ``GetFileDownloadUrlQuery``, который возвращает presigned URL
    к S3/MinIO (требует, чтобы у клиента был сетевой доступ к самому хранилищу),
    этот запрос возвращает байты файла, чтобы их можно было отдать через
    обычный HTTP-эндпоинт API. Удобно для:

    - мобильных клиентов, у которых нет доступа к внутренней сети S3;
    - превью изображений в чате/комментариях.
    """

    file_id: str
    caller_id: str


class FileContentResult:
    """Результат: байты + метаданные файла."""

    def __init__(
        self,
        *,
        data: bytes,
        name: str,
        mime_type: str,
        size_bytes: int,
        file_id: str,
    ) -> None:
        self.data = data
        self.name = name
        self.mime_type = mime_type
        self.size_bytes = size_bytes
        self.file_id = file_id


class GetFileContentHandler(BaseQueryHandler[GetFileContentQuery, FileContentResult]):
    """
    Чтение содержимого файла из хранилища через API.

    Логика проверок (статус, антивирус, разрешения) полностью совпадает с
    `GetFileDownloadUrlHandler` — мы лишь возвращаем байты вместо URL.

    Эмитит событие `FileDownloaded` (через event_bus), как и presigned-вариант:
    с точки зрения аудита это та же операция «пользователь получил файл».
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

    async def handle(self, query: GetFileContentQuery) -> FileContentResult:
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
        data = await self._file_storage.download(key=file.storage_path)
        await self._event_bus.publish(
            FileDownloaded(file_id=str(file.id), downloader_id=query.caller_id)
        )
        return FileContentResult(
            data=data,
            name=file.name,
            mime_type=file.mime_type,
            size_bytes=file.size.value,
            file_id=str(file.id),
        )

from __future__ import annotations

from app.core.logging import get_logger
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.application.ports.file_storage.file_storage_port import (
    FileStoragePort,
)
from app.shared.application.ports.security.virus_scanner_port import (
    ScanVerdict,
    VirusScannerPort,
)
from app.shared.domain.value_objects.id_vo import Id

from app.context.filestorage.domain.exceptions.file_exceptions import (
    FileNotFoundException,
)
from app.context.filestorage.domain.repositories.file_repository import FileRepository
from app.context.filestorage.domain.value_objects.file_status import FileStatus
from app.context.filestorage.domain.value_objects.virus_scan_status import (
    VirusScanStatus,
)

logger = get_logger(__name__)


class ScanFileService:
    """
    Внутренний use case: сканирование файла антивирусом.

    Используется Celery-таском (background) — **без RBAC-проверок**,
    так как вызывается системой, а не пользователем.

    Пайплайн:
        1. Загружает агрегат ``File``.
        2. Скачивает blob из S3 через ``FileStoragePort``.
        3. Передаёт байты в ``VirusScannerPort.scan_bytes(...)``.
        4. По вердикту вызывает ``file.mark_scan_clean()`` /
           ``mark_scan_infected(virus_name)`` / ``mark_scan_error()``.
        5. Сохраняет агрегат и публикует доменные события
           (``VirusScanCompleted`` / ``VirusDetected``).
    """

    def __init__(
        self,
        file_repo: FileRepository,
        file_storage: FileStoragePort,
        virus_scanner: VirusScannerPort,
        event_bus: DomainEventBus,
    ) -> None:
        self._file_repo = file_repo
        self._file_storage = file_storage
        self._virus_scanner = virus_scanner
        self._event_bus = event_bus

    async def scan(self, file_id: str) -> None:
        file = await self._file_repo.get_by_id(Id.from_string(file_id))
        if file is None:
            raise FileNotFoundException(id=file_id)

        # Skip уже-просканированные / удалённые файлы.
        if file.status == FileStatus.DELETED:
            logger.info("Skipping scan: file deleted", file_id=file_id)
            return
        if file.scan_status != VirusScanStatus.PENDING:
            logger.info(
                "Skipping scan: already scanned",
                file_id=file_id,
                scan_status=file.scan_status.value,
            )
            return

        # Скачиваем blob.
        try:
            data = await self._file_storage.download(file.storage_path)
        except Exception as exc:  # noqa: BLE001
            logger.error(
                "Failed to download file for scan",
                file_id=file_id,
                storage_path=file.storage_path,
                error=str(exc),
            )
            file.mark_scan_error()
            await self._file_repo.update(file)
            await self._event_bus.publish_all(file.clear_domain_events())
            return

        # Сканируем.
        result = await self._virus_scanner.scan_bytes(data=data, filename=file.name)

        if result.verdict == ScanVerdict.CLEAN:
            file.mark_scan_clean()
        elif result.verdict == ScanVerdict.INFECTED:
            file.mark_scan_infected(virus_name=result.virus_name or "UNKNOWN")
        elif result.verdict == ScanVerdict.SKIPPED:
            # Доменный enum имеет SKIPPED — но домен не предоставляет публичный
            # метод (skipped — это эквивалент error по семантике невозможности
            # завершить скан). Остановимся на mark_scan_error.
            file.mark_scan_error()
        else:
            file.mark_scan_error()

        await self._file_repo.update(file)
        await self._event_bus.publish_all(file.clear_domain_events())
        logger.info(
            "File scan completed",
            file_id=file_id,
            verdict=result.verdict.value,
            scanner=result.scanner,
        )

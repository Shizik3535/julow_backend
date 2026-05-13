from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class ReportAttachmentUploadResult:
    """Результат загрузки готового отчёта через FileStorage BC."""

    file_id: str
    url: str
    storage_path: str
    size_bytes: int


class FileAttachmentPort(ABC):
    """
    Inboard-порт: загрузка готовых файлов отчётов через FileStorage BC.

    Analytics BC **не загружает файлы напрямую в S3** — вместо этого
    делегирует FileStorage BC, который:
        - создаёт агрегат ``File`` в ``fs_files`` (workspace, владелец,
          тип, ``scan_status``);
        - учитывает квоту хранилища workspace
          (``StorageQuotaExceededException``);
        - проверяет ``max_file_size_bytes`` / ``allowed_file_types``;
        - эмитит ``FileUploaded`` (антивирус, аудит, аналитика);
        - возвращает реальный ``file_id``, по которому файл доступен через
          обычный FileStorage API (скачивание, шеринг, удаление).

    Используется воркером ``ReportRenderSchedulerPort``: после
    рендеринга `AnalyticsResult` в файл (PDF/Excel/CSV/PNG/...) воркер
    отдаёт байты в этот порт, получает ``file_id`` + URL и записывает их
    в ``analytics_report_jobs.download_url``.

    Адаптер реализации находится в infrastructure-слое Analytics BC и
    делегирует в outboard ``FileAttachmentProvider`` (FileStorage BC).
    """

    @abstractmethod
    async def upload_report(
        self,
        *,
        workspace_id: str,
        uploader_id: str,
        filename: str,
        file_data: bytes,
        content_type: str,
    ) -> ReportAttachmentUploadResult:
        """Сохранить готовый отчёт в FileStorage BC; вернуть метаданные с
        реальным ``file_id``."""

    @abstractmethod
    async def get_report_url(
        self, file_id: str, expires_in: int | None = 3600
    ) -> str | None:
        """Получить подписанный URL для скачивания отчёта.

        ``expires_in=None`` — публичный URL (если поддерживается storage).
        Возвращает ``None``, если файла нет (например, протух TTL и
        был удалён).
        """

    @abstractmethod
    async def delete_report(self, file_id: str) -> None:
        """Окончательно удалить отчёт из FileStorage BC.

        Идемпотентно: если файл не найден — без ошибки. Освобождает
        квоту workspace и эмитит ``FileDeleted``.
        """

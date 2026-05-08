from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class TaskAttachmentUploadResult:
    """Результат загрузки вложения через FileStorage BC."""

    file_id: str
    url: str
    storage_path: str
    size_bytes: int


class FileAttachmentPort(ABC):
    """
    Inboard-порт: делегирование загрузки вложений в FileStorage BC.

    Task BC не загружает файлы напрямую в S3 — вместо этого вызывает
    FileStorage BC, который создаёт агрегат ``File`` (учёт квоты,
    события, антивирус, RBAC ``files.*``).

    Адаптер в infrastructure-слое Task BC делегирует в outboard
    ``FileAttachmentProvider`` (FileStorage BC).
    """

    @abstractmethod
    async def upload_attachment(
        self,
        *,
        workspace_id: str,
        uploader_id: str,
        filename: str,
        file_data: bytes,
        content_type: str,
    ) -> TaskAttachmentUploadResult:
        """Загрузить файл, вернуть метаданные с реальным ``file_id``."""

    @abstractmethod
    async def delete_attachment(self, file_id: str) -> None:
        """Окончательно удалить вложение из FileStorage BC (идемпотентно)."""

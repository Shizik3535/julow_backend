from __future__ import annotations

from datetime import datetime

from app.shared.application.base_dto import BaseDTO


class AttachmentDTO(BaseDTO):
    """
    DTO вложения (Communication BC).

    Атрибуты:
        id: UUID вложения.
        file_id: UUID файла из FileStorage BC.
        url: URL файла.
        attachment_type: Тип вложения (image/video/file/link/voice).
        name: Имя файла.
        size_bytes: Размер в байтах.
        preview_url: URL превью (если есть).
        created_at: Время создания.
    """

    id: str
    file_id: str
    url: str | None = None
    attachment_type: str = "file"
    name: str = ""
    size_bytes: int = 0
    preview_url: str | None = None
    created_at: datetime | None = None

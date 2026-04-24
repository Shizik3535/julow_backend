from __future__ import annotations

from app.shared.application.base_dto import BaseDTO


class FileInfo(BaseDTO):
    """
    Информация о файле в хранилище.

    Атрибуты:
        key: Ключ файла в хранилище.
        size: Размер файла в байтах.
        content_type: MIME-тип файла.
    """

    key: str
    size: int
    content_type: str

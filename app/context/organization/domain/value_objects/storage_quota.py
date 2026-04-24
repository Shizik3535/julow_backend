from __future__ import annotations

from dataclasses import dataclass, field

from app.shared.domain.base_value_object import ValueObject
from app.shared.domain.exceptions import ValidationException


@dataclass(frozen=True)
class StorageQuota(ValueObject):
    """
    Квота хранилища организации.

    Атрибуты:
        max_bytes: Максимальный объём в байтах.
        used_bytes: Использованный объём в байтах.
        max_file_size_bytes: Максимальный размер одного файла (None — без ограничения).
        allowed_extensions: Разрешённые расширения файлов (None — все).
    """

    max_bytes: int = 0
    used_bytes: int = 0
    max_file_size_bytes: int | None = None
    allowed_extensions: list[str] | None = None

    def __post_init__(self) -> None:
        if self.max_bytes < 0:
            raise ValidationException(
                field="max_bytes",
                message="Максимальный объём не может быть отрицательным",
            )
        if self.used_bytes < 0:
            raise ValidationException(
                field="used_bytes",
                message="Использованный объём не может быть отрицательным",
            )
        if self.used_bytes > self.max_bytes:
            raise ValidationException(
                field="used_bytes",
                message="Использованный объём превышает максимальный",
            )
        if self.max_file_size_bytes is not None and self.max_file_size_bytes < 0:
            raise ValidationException(
                field="max_file_size_bytes",
                message="Максимальный размер файла не может быть отрицательным",
            )

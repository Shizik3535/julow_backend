from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_value_object import ValueObject
from app.shared.domain.exceptions import ValidationException


@dataclass(frozen=True)
class FileSize(ValueObject):
    """
    Value Object для размера файла.

    Атрибуты:
        value: Размер в байтах (≥0).
    """

    value: int = 0

    def __post_init__(self) -> None:
        if self.value < 0:
            raise ValidationException(
                field="file_size",
                message=f"Размер файла не может быть отрицательным: {self.value}",
            )

    def __str__(self) -> str:
        if self.value < 1024:
            return f"{self.value} B"
        elif self.value < 1024 * 1024:
            return f"{self.value / 1024:.1f} KB"
        elif self.value < 1024 * 1024 * 1024:
            return f"{self.value / (1024 * 1024):.1f} MB"
        else:
            return f"{self.value / (1024 * 1024 * 1024):.1f} GB"

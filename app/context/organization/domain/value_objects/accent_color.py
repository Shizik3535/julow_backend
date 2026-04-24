from __future__ import annotations

import re
from dataclasses import dataclass

from app.shared.domain.base_value_object import ValueObject
from app.shared.domain.exceptions import ValidationException

_HEX_COLOR_PATTERN = re.compile(r"^#[0-9a-fA-F]{6}$")


@dataclass(frozen=True)
class AccentColor(ValueObject):
    """
    Value Object для акцентного цвета организации.

    Гарантирует, что значение является валидным HEX-кодом цвета (#RRGGBB).
    Хранится в верхнем регистре для единообразия.

    Атрибуты:
        hex: HEX-код цвета.
    """

    hex: str

    def __post_init__(self) -> None:
        normalized = self.hex.strip().upper()
        object.__setattr__(self, "hex", normalized)
        if not _HEX_COLOR_PATTERN.match(normalized):
            raise ValidationException(
                field="accent_color",
                message=f"Некорректный HEX-код цвета: {normalized}",
            )

    def __str__(self) -> str:
        return self.hex

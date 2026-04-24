from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_value_object import ValueObject
from app.shared.domain.value_objects.color_vo import Color


@dataclass(frozen=True)
class Category(ValueObject):
    """
    Value Object для категории проекта.

    Атрибуты:
        name: Название категории.
        color: Цвет категории (из shared kernel).
    """

    name: str
    color: Color | None = None

    def __str__(self) -> str:
        return self.name

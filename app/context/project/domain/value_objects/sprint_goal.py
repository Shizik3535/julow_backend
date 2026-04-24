from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_value_object import ValueObject


@dataclass(frozen=True)
class SprintGoal(ValueObject):
    """
    Value Object для цели спринта.

    Атрибуты:
        value: Текстовое описание цели спринта.
    """

    value: str

    def __str__(self) -> str:
        return self.value

from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_value_object import ValueObject
from app.shared.domain.exceptions import ValidationException


@dataclass(frozen=True)
class WIPLimit(ValueObject):
    """
    Value Object для WIP-лимита (Work In Progress).

    Атрибуты:
        value: Максимальное количество задач в колонке (≥1).
    """

    value: int

    def __post_init__(self) -> None:
        if self.value < 1:
            raise ValidationException(
                field="wip_limit",
                message="WIP-лимит должен быть не менее 1",
            )

    def __str__(self) -> str:
        return str(self.value)

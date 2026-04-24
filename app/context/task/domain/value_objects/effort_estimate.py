from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_value_object import ValueObject
from app.shared.domain.exceptions import ValidationException
from app.context.task.domain.value_objects.effort_unit import EffortUnit


@dataclass(frozen=True)
class EffortEstimate(ValueObject):
    """
    Value Object для оценки усилия.

    Атрибуты:
        value: Числовое значение оценки.
        unit: Единица измерения.
    """

    value: float = 0.0
    unit: EffortUnit = EffortUnit.HOURS

    def __post_init__(self) -> None:
        if self.value < 0:
            raise ValidationException(
                field="effort_estimate",
                message="Оценка усилия не может быть отрицательной",
            )

from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_value_object import ValueObject
from app.shared.domain.exceptions import ValidationException
from app.context.task.domain.value_objects.effort_unit import EffortUnit


@dataclass(frozen=True)
class ActualEffort(ValueObject):
    """
    Value Object для фактического усилия.

    Атрибуты:
        value: Числовое значение фактического усилия.
        unit: Единица измерения.
    """

    value: float = 0.0
    unit: EffortUnit = EffortUnit.HOURS

    def __post_init__(self) -> None:
        if self.value < 0:
            raise ValidationException(
                field="actual_effort",
                message="Фактическое усилие не может быть отрицательным",
            )

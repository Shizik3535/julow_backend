from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from app.shared.domain.base_value_object import ValueObject
from app.shared.domain.exceptions import ValidationException


@dataclass(frozen=True)
class Percent(ValueObject):
    """
    Value Object для процентного значения.

    Гарантирует, что значение находится в диапазоне от 0 до 100.

    Атрибуты:
        value: Процентное значение (0–100).

    Пример:
        discount = Percent(Decimal("15.5"))
    """

    value: Decimal

    def __post_init__(self) -> None:
        if not isinstance(self.value, Decimal):
            raise ValidationException(
                field="percent",
                message="Значение должно быть типа Decimal",
            )
        if self.value < 0 or self.value > 100:
            raise ValidationException(
                field="percent",
                message=f"Процент должен быть от 0 до 100: {self.value}",
            )

    def __str__(self) -> str:
        return f"{self.value}%"

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from app.shared.domain.base_value_object import ValueObject
from app.shared.domain.exceptions import ValidationException


@dataclass(frozen=True)
class DateRange(ValueObject):
    """
    Value Object для диапазона дат.

    Гарантирует, что начальная дата не позже конечной.

    Атрибуты:
        start: Начальная дата диапазона.
        end: Конечная дата диапазона.

    Пример:
        period = DateRange(date(2025, 1, 1), date(2025, 12, 31))
    """

    start: date
    end: date

    def __post_init__(self) -> None:
        if self.start > self.end:
            raise ValidationException(
                field="date_range",
                message=f"Начальная дата ({self.start}) позже конечной ({self.end})",
            )

    def __str__(self) -> str:
        return f"{self.start} – {self.end}"

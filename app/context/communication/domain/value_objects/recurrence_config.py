from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from app.shared.domain.base_value_object import ValueObject
from app.shared.domain.exceptions import ValidationException
from app.context.communication.domain.value_objects.recurrence_pattern import RecurrencePattern


@dataclass(frozen=True)
class RecurrenceConfig(ValueObject):
    """
    Конфигурация повторения совещания.

    Дубликат из Task BC — может расходиться в будущем.

    Атрибуты:
        pattern: Паттерн повторения.
        interval: Интервал (каждые N дней/недель/...).
        end_date: Дата окончания повторений (None — бесконечно).
        max_occurrences: Максимальное количество повторений (None — бесконечно).
    """

    pattern: RecurrencePattern = RecurrencePattern.WEEKLY
    interval: int = 1
    end_date: date | None = None
    max_occurrences: int | None = None

    def __post_init__(self) -> None:
        if self.interval < 1:
            raise ValidationException(
                field="recurrence_interval",
                message="Интервал повторения должен быть не менее 1",
            )
        if self.max_occurrences is not None and self.max_occurrences < 1:
            raise ValidationException(
                field="recurrence_max_occurrences",
                message="Максимальное количество повторений должно быть не менее 1",
            )

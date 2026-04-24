from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_value_object import ValueObject
from app.shared.domain.exceptions import ValidationException


@dataclass(frozen=True)
class LockoutThreshold(ValueObject):
    """
    Value Object для порога блокировки.

    Определяет, после какого количества неудачных попыток
    и на какой длительности происходит блокировка.

    Атрибуты:
        failed_attempts: Количество неудачных попыток для срабатывания.
        lock_duration_minutes: Длительность блокировки в минутах.
    """

    failed_attempts: int
    lock_duration_minutes: int

    def __post_init__(self) -> None:
        if self.failed_attempts < 1:
            raise ValidationException(
                field="failed_attempts",
                message="Количество неудачных попыток должно быть >= 1",
            )
        if self.lock_duration_minutes < 1:
            raise ValidationException(
                field="lock_duration_minutes",
                message="Длительность блокировки должна быть >= 1 минуты",
            )

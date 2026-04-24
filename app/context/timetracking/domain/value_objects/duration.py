from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_value_object import ValueObject
from app.shared.domain.exceptions import ValidationException


@dataclass(frozen=True)
class Duration(ValueObject):
    """
    Value Object для длительности.

    Атрибуты:
        seconds: Количество секунд (≥0).
    """

    seconds: int = 0

    def __post_init__(self) -> None:
        if self.seconds < 0:
            raise ValidationException(
                field="duration",
                message=f"Длительность не может быть отрицательной: {self.seconds}",
            )

    @property
    def hours(self) -> float:
        return self.seconds / 3600

    @property
    def minutes(self) -> float:
        return self.seconds / 60

    def __str__(self) -> str:
        h = self.seconds // 3600
        m = (self.seconds % 3600) // 60
        s = self.seconds % 60
        return f"{h:02d}:{m:02d}:{s:02d}"

from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_value_object import ValueObject
from app.shared.domain.exceptions import ValidationException


@dataclass(frozen=True)
class TaskProgress(ValueObject):
    """
    Value Object для прогресса задачи (0–100%).

    Атрибуты:
        value: Процент выполнения (0–100).
    """

    value: int = 0

    def __post_init__(self) -> None:
        if self.value < 0 or self.value > 100:
            raise ValidationException(
                field="task_progress",
                message=f"Прогресс должен быть от 0 до 100: {self.value}",
            )

    def __str__(self) -> str:
        return f"{self.value}%"

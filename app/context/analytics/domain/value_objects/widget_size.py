from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_value_object import ValueObject
from app.shared.domain.exceptions import ValidationException


@dataclass(frozen=True)
class WidgetSize(ValueObject):
    """Размер виджета на grid (1–12)."""

    cols: int = 6
    rows: int = 4

    def __post_init__(self) -> None:
        if not (1 <= self.cols <= 12):
            raise ValidationException(field="widget_size_cols", message=f"cols должен быть 1–12: {self.cols}")
        if not (1 <= self.rows <= 12):
            raise ValidationException(field="widget_size_rows", message=f"rows должен быть 1–12: {self.rows}")

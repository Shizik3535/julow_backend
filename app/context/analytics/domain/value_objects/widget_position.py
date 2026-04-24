from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_value_object import ValueObject


@dataclass(frozen=True)
class WidgetPosition(ValueObject):
    """Позиция виджета на grid."""

    row: int = 0
    col: int = 0

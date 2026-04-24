from __future__ import annotations

from dataclasses import dataclass, field

from app.shared.domain.base_value_object import ValueObject
from app.shared.domain.value_objects.id_vo import Id


@dataclass(frozen=True)
class TaskOrder(ValueObject):
    """
    Value Object для позиции задачи на доске.

    Атрибуты:
        position: Позиция (float для вставки между позициями).
        column_id: Opaque ID колонки из Board AR (Project BC).
    """

    position: float = 0.0
    column_id: Id = field(default_factory=Id.generate)

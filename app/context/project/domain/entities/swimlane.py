from __future__ import annotations

from dataclasses import dataclass, field

from app.shared.domain.base_entity import BaseEntity
from app.context.project.domain.value_objects.swimlane_group_by import SwimlaneGroupBy


@dataclass
class Swimlane(BaseEntity):
    """
    Сущность swimlane на доске.

    Принадлежит агрегату Board.

    Атрибуты:
        name: Название swimlane.
        order: Порядок.
        group_by: Способ группировки.
        group_value: Значение группировки (None — все).
    """

    name: str = ""
    order: int = 0
    group_by: SwimlaneGroupBy = SwimlaneGroupBy.ASSIGNEE
    group_value: str | None = None

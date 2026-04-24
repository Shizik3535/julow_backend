from __future__ import annotations

from dataclasses import dataclass, field

from app.shared.domain.base_entity import BaseEntity
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.color_vo import Color
from app.context.project.domain.value_objects.wip_limit import WIPLimit


@dataclass
class BoardColumn(BaseEntity):
    """
    Сущность колонки доски.

    Принадлежит агрегату Board.

    Атрибуты:
        name: Название колонки.
        order: Порядок колонки.
        color: Цвет колонки (из shared kernel).
        wip_limit: WIP-лимит (None — без ограничения).
        status_mapping: ID workflow-статуса для связи.
    """

    name: str = ""
    order: int = 0
    color: Color | None = None
    wip_limit: WIPLimit | None = None
    status_mapping: Id | None = None

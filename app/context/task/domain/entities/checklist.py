from __future__ import annotations

from dataclasses import dataclass, field

from app.shared.domain.base_entity import BaseEntity
from app.context.task.domain.entities.checklist_item import ChecklistItem


@dataclass
class Checklist(BaseEntity):
    """
    Сущность чек-листа внутри задачи.

    Принадлежит агрегату Task.

    Атрибуты:
        title: Заголовок чек-листа.
        items: Список пунктов.
    """

    title: str = ""
    items: list[ChecklistItem] = field(default_factory=list)

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone

from app.shared.domain.base_entity import BaseEntity
from app.shared.domain.value_objects.id_vo import Id


@dataclass
class ChecklistItem(BaseEntity):
    """
    Сущность пункта чек-листа.

    Принадлежит Checklist (внутри Task).

    Атрибуты:
        text: Текст пункта.
        is_checked: Отмечен ли пункт.
        assignee_id: ID исполнителя.
        due_date: Срок выполнения.
        checked_at: Время отметки.
        order: Порядок пункта.
    """

    text: str = ""
    is_checked: bool = False
    assignee_id: Id | None = None
    due_date: date | None = None
    checked_at: datetime | None = None
    order: int = 0

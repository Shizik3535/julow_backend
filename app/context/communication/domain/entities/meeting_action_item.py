from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from app.shared.domain.base_entity import BaseEntity
from app.shared.domain.value_objects.id_vo import Id


@dataclass
class MeetingActionItem(BaseEntity):
    """
    Сущность action item совещания.

    Принадлежит агрегату Meeting.

    Атрибуты:
        text: Текст задачи.
        assignee_id: ID исполнителя.
        due_date: Срок выполнения.
        is_completed: Завершён ли.
    """

    text: str = ""
    assignee_id: Id | None = None
    due_date: date | None = None
    is_completed: bool = False

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone

from app.shared.domain.base_entity import BaseEntity
from app.shared.domain.value_objects.rich_text_vo import RichText
from app.context.project.domain.value_objects.milestone_status import MilestoneStatus


@dataclass
class Milestone(BaseEntity):
    """
    Сущность milestone проекта.

    Принадлежит агрегату Project.

    Атрибуты:
        name: Название milestone.
        description: Описание (форматированный текст).
        status: Статус milestone.
        due_date: Срок выполнения.
        completed_at: Время завершения.
    """

    name: str = ""
    description: RichText | None = None
    status: MilestoneStatus = MilestoneStatus.NOT_STARTED
    due_date: date = field(default_factory=date.today)
    completed_at: datetime | None = None

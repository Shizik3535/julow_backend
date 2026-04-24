from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_entity import BaseEntity
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.rich_text_vo import RichText


@dataclass
class MeetingNote(BaseEntity):
    """
    Сущность заметки совещания.

    Принадлежит агрегату Meeting.

    Атрибуты:
        content: Содержание заметки.
        author_id: ID автора.
        created_at: Время создания.
    """

    content: RichText | None = None
    author_id: Id = field(default_factory=Id.generate)
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

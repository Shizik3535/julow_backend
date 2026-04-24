from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_entity import BaseEntity
from app.shared.domain.value_objects.id_vo import Id


@dataclass
class RetroItem(BaseEntity):
    """
    Сущность элемента ретроспективы.

    Принадлежит SprintRetro (внутри Sprint).

    Атрибуты:
        section_id: ID секции ретроспективы.
        content: Содержание элемента.
        author_id: ID автора.
        votes: Количество голосов.
        created_at: Время создания.
    """

    section_id: Id = field(default_factory=Id.generate)
    content: str = ""
    author_id: Id = field(default_factory=Id.generate)
    votes: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

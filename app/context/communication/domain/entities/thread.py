from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_entity import BaseEntity
from app.shared.domain.value_objects.id_vo import Id


@dataclass
class Thread(BaseEntity):
    """
    Сущность треда внутри чата.

    Принадлежит агрегату Chat.

    Атрибуты:
        parent_message_id: ID родительского сообщения.
        title: Заголовок треда.
        is_resolved: Закрыт ли тред.
        created_at: Время создания.
    """

    parent_message_id: Id = field(default_factory=Id.generate)
    title: str | None = None
    is_resolved: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

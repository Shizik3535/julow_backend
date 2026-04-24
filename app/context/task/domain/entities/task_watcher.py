from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_entity import BaseEntity
from app.shared.domain.value_objects.id_vo import Id


@dataclass
class TaskWatcher(BaseEntity):
    """
    Сущность наблюдателя задачи.

    Принадлежит агрегату Task.

    Атрибуты:
        user_id: ID пользователя-наблюдателя.
        watched_at: Время подписки.
    """

    user_id: Id = field(default_factory=Id.generate)
    watched_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

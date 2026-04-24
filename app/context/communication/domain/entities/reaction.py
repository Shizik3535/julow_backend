from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_entity import BaseEntity
from app.shared.domain.value_objects.id_vo import Id
from app.context.communication.domain.value_objects.reaction_emoji import ReactionEmoji


@dataclass
class Reaction(BaseEntity):
    """
    Сущность реакции (emoji).

    Используется в Comment и Message. Уникальность по (user_id, emoji).

    Атрибуты:
        user_id: ID пользователя.
        emoji: Emoji реакция.
        created_at: Время создания.
    """

    user_id: Id = field(default_factory=Id.generate)
    emoji: ReactionEmoji = field(default_factory=ReactionEmoji)
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

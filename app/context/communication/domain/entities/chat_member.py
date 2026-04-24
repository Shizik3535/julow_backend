from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_entity import BaseEntity
from app.shared.domain.value_objects.id_vo import Id
from app.context.communication.domain.value_objects.chat_member_role import ChatMemberRole


@dataclass
class ChatMember(BaseEntity):
    """
    Сущность участника чата.

    Принадлежит агрегату Chat.

    Атрибуты:
        user_id: ID пользователя.
        role: Роль в чате.
        joined_at: Время присоединения.
        last_read_at: Время последнего прочтения.
    """

    user_id: Id = field(default_factory=Id.generate)
    role: ChatMemberRole = ChatMemberRole.MEMBER
    joined_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    last_read_at: datetime | None = None

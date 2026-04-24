from __future__ import annotations

from enum import Enum


class ChatMemberRole(Enum):
    """
    Роль участника чата.

    Значения:
        MEMBER: Обычный участник
        ADMIN: Администратор
        OWNER: Владелец (создатель)
    """

    MEMBER = "member"
    ADMIN = "admin"
    OWNER = "owner"

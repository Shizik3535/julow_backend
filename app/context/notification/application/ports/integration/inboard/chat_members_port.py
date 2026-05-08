from __future__ import annotations

from abc import ABC, abstractmethod


class ChatMembersPort(ABC):
    """
    Inboard-порт: получение участников чата из Communication BC.

    Notification BC использует для определения получателей уведомлений
    при событиях ``MessageSent``, ``ChatMemberAdded`` и т.д.
    """

    @abstractmethod
    async def get_chat_member_ids(self, chat_id: str) -> list[str]:
        """Вернуть список ``user_id`` всех участников чата."""

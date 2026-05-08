from __future__ import annotations

from abc import ABC, abstractmethod


class ChatMembersProvider(ABC):
    """
    Outboard-порт: участники чата для внешних BC.

    Реализуется в infrastructure-слое Communication BC.
    Notification BC инжектит inboard-порт, адаптер которого делегирует
    в этот provider — так определяются получатели уведомлений
    при событиях ``MessageSent`` / ``ChatMemberAdded`` и т.д.
    """

    @abstractmethod
    async def get_chat_member_ids(self, chat_id: str) -> list[str]:
        """Вернуть список ``user_id`` всех участников чата."""

from __future__ import annotations

from app.context.communication.application.ports.integration.outboard.chat_members_provider import (
    ChatMembersProvider,
)
from app.context.notification.application.ports.integration.inboard.chat_members_port import (
    ChatMembersPort,
)


class ChatMembersAdapter(ChatMembersPort):
    """
    Реализация inboard-порта ``ChatMembersPort`` для Notification BC.

    Делегирует получение участников в outboard-порт Communication BC
    (``ChatMembersProvider``).
    """

    def __init__(self, chat_members_provider: ChatMembersProvider) -> None:
        self._provider = chat_members_provider

    async def get_chat_member_ids(self, chat_id: str) -> list[str]:
        return await self._provider.get_chat_member_ids(chat_id=chat_id)

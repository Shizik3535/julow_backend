from __future__ import annotations

from app.shared.domain.value_objects.id_vo import Id

from app.context.communication.application.ports.integration.outboard.chat_members_provider import (
    ChatMembersProvider,
)
from app.context.communication.domain.repositories.chat_repository import (
    ChatRepository,
)


class ChatMembersProviderAdapter(ChatMembersProvider):
    """Реализация outboard-порта ``ChatMembersProvider`` через ``ChatRepository``."""

    def __init__(self, repo: ChatRepository) -> None:
        self._repo = repo

    async def get_chat_member_ids(self, chat_id: str) -> list[str]:
        chat = await self._repo.get_by_id(Id.from_string(chat_id))
        if chat is None:
            return []
        return [str(m.user_id) for m in chat.members]

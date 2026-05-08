"""Запрос всех чатов пользователя."""

from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id

from app.context.communication.application.dto.chat_dto import ChatListDTO
from app.context.communication.application.dto.mappers import chat_to_dto
from app.context.communication.domain.repositories.chat_repository import (
    ChatRepository,
)


class GetMyChatsQuery(BaseQuery):
    """Запрос чатов пользователя."""

    caller_id: str
    include_archived: bool = False


class GetMyChatsHandler(BaseQueryHandler[GetMyChatsQuery, ChatListDTO]):
    def __init__(self, chat_repo: ChatRepository) -> None:
        super().__init__()
        self._repo = chat_repo

    async def handle(self, query: GetMyChatsQuery) -> ChatListDTO:
        chats = await self._repo.get_by_member(Id.from_string(query.caller_id))
        if not query.include_archived:
            chats = [c for c in chats if not c.is_archived]
        items = [chat_to_dto(c) for c in chats]
        return ChatListDTO(items=items, total=len(items))

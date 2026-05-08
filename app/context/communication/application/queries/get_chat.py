"""Запрос чата по ID."""

from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id

from app.context.communication.application.dto.chat_dto import ChatDTO
from app.context.communication.application.dto.mappers import chat_to_dto
from app.context.communication.domain.exceptions.chat_exceptions import (
    ChatNotFoundException,
    NotChatMemberException,
)
from app.context.communication.domain.repositories.chat_repository import (
    ChatRepository,
)


class GetChatQuery(BaseQuery):
    """Запрос чата по ID (только для участников)."""

    chat_id: str
    caller_id: str


class GetChatHandler(BaseQueryHandler[GetChatQuery, ChatDTO]):
    def __init__(self, chat_repo: ChatRepository) -> None:
        super().__init__()
        self._repo = chat_repo

    async def handle(self, query: GetChatQuery) -> ChatDTO:
        chat = await self._repo.get_by_id(Id.from_string(query.chat_id))
        if chat is None:
            raise ChatNotFoundException(query.chat_id)
        if not any(str(m.user_id) == query.caller_id for m in chat.members):
            raise NotChatMemberException()
        return chat_to_dto(chat)

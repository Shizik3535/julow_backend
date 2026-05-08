"""Запрос сообщений чата с пагинацией."""

from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id

from app.context.communication.application.dto.mappers import message_to_dto
from app.context.communication.application.dto.message_dto import MessageListDTO
from app.context.communication.domain.exceptions.chat_exceptions import (
    ChatNotFoundException,
    NotChatMemberException,
)
from app.context.communication.domain.repositories.chat_repository import (
    ChatRepository,
)
from app.context.communication.domain.repositories.message_repository import (
    MessageRepository,
)


class GetMessagesByChatQuery(BaseQuery):
    """Запрос сообщений чата с offset/limit."""

    chat_id: str
    caller_id: str
    offset: int = 0
    limit: int = 50
    include_deleted: bool = False


class GetMessagesByChatHandler(
    BaseQueryHandler[GetMessagesByChatQuery, MessageListDTO]
):
    def __init__(
        self,
        chat_repo: ChatRepository,
        message_repo: MessageRepository,
    ) -> None:
        super().__init__()
        self._chat_repo = chat_repo
        self._message_repo = message_repo

    async def handle(self, query: GetMessagesByChatQuery) -> MessageListDTO:
        chat = await self._chat_repo.get_by_id(Id.from_string(query.chat_id))
        if chat is None:
            raise ChatNotFoundException(query.chat_id)
        if not any(str(m.user_id) == query.caller_id for m in chat.members):
            raise NotChatMemberException()

        messages = await self._message_repo.get_by_chat(
            chat_id=Id.from_string(query.chat_id),
            offset=query.offset,
            limit=query.limit,
        )
        if not query.include_deleted:
            messages = [m for m in messages if not m.is_deleted]

        items = [message_to_dto(m) for m in messages]
        return MessageListDTO(
            items=items,
            total=len(items),
            has_more=len(messages) >= query.limit,
        )

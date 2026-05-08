"""Запрос количества непрочитанных сообщений в чате."""

from __future__ import annotations

from datetime import datetime, timezone

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id

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


_EPOCH = datetime.fromtimestamp(0, tz=timezone.utc)


class CountUnreadMessagesQuery(BaseQuery):
    """Подсчитать непрочитанные сообщения для caller_id в указанном чате."""

    chat_id: str
    caller_id: str


class CountUnreadMessagesHandler(BaseQueryHandler[CountUnreadMessagesQuery, int]):
    def __init__(
        self,
        chat_repo: ChatRepository,
        message_repo: MessageRepository,
    ) -> None:
        super().__init__()
        self._chat_repo = chat_repo
        self._message_repo = message_repo

    async def handle(self, query: CountUnreadMessagesQuery) -> int:
        chat = await self._chat_repo.get_by_id(Id.from_string(query.chat_id))
        if chat is None:
            raise ChatNotFoundException(query.chat_id)

        member = next(
            (m for m in chat.members if str(m.user_id) == query.caller_id),
            None,
        )
        if member is None:
            raise NotChatMemberException()

        after = member.last_read_at or _EPOCH
        return await self._message_repo.count_unread(
            chat_id=Id.from_string(query.chat_id),
            after=after,
        )

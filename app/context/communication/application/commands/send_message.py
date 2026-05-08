"""Команда отправки сообщения в чат."""

from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.rich_text_format import RichTextFormat
from app.shared.domain.value_objects.rich_text_vo import RichText

from app.context.communication.application.dto.mappers import message_to_dto
from app.context.communication.application.dto.message_dto import MessageDTO
from app.context.communication.application.exceptions.authorization_exceptions import (
    CannotPostToAnnouncementException,
)
from app.context.communication.domain.aggregates.message import Message
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
from app.context.communication.domain.value_objects.chat_member_role import (
    ChatMemberRole,
)
from app.context.communication.domain.value_objects.chat_type import ChatType
from app.context.communication.domain.value_objects.message_type import MessageType


_ANNOUNCEMENT_ALLOWED = {ChatMemberRole.OWNER, ChatMemberRole.ADMIN}


class SendMessageCommand(BaseCommand):
    """
    Отправить сообщение в чат.

    Атрибуты:
        caller_id: ID отправителя.
        chat_id: ID чата.
        content: Текст (markdown).
        content_format: Формат содержимого.
        thread_id: ID треда (None — основной чат).
        reply_to_id: ID сообщения, на которое отвечают.
        message_type: Тип сообщения.
    """

    caller_id: str
    chat_id: str
    content: str | None = None
    content_format: str = "markdown"
    thread_id: str | None = None
    reply_to_id: str | None = None
    message_type: str = "text"


class SendMessageHandler(BaseCommandHandler[SendMessageCommand, MessageDTO]):
    """Обработчик отправки сообщения."""

    def __init__(
        self,
        chat_repo: ChatRepository,
        message_repo: MessageRepository,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._chat_repo = chat_repo
        self._message_repo = message_repo
        self._event_bus = event_bus

    async def handle(self, command: SendMessageCommand) -> MessageDTO:
        chat = await self._chat_repo.get_by_id(Id.from_string(command.chat_id))
        if chat is None:
            raise ChatNotFoundException(command.chat_id)

        if chat.is_archived:
            raise NotChatMemberException()  # переиспользуем — чат недоступен

        member = next(
            (m for m in chat.members if str(m.user_id) == command.caller_id),
            None,
        )
        if member is None:
            raise NotChatMemberException()

        if (
            chat.chat_type == ChatType.ANNOUNCEMENT
            and member.role not in _ANNOUNCEMENT_ALLOWED
        ):
            raise CannotPostToAnnouncementException()

        content: RichText | None = None
        if command.content is not None:
            content = RichText(
                content=command.content,
                format=RichTextFormat(command.content_format),
            )

        message = Message.create(
            chat_id=Id.from_string(command.chat_id),
            sender_id=Id.from_string(command.caller_id),
            content=content,
            message_type=MessageType(command.message_type),
            thread_id=Id.from_string(command.thread_id) if command.thread_id else None,
            reply_to_id=(
                Id.from_string(command.reply_to_id) if command.reply_to_id else None
            ),
        )
        await self._message_repo.add(message)

        # Обновляем last_message_at в чате
        chat.last_message_at = message.created_at
        await self._chat_repo.update(chat)

        await self._event_bus.publish_all(message.clear_domain_events())
        await self._event_bus.publish_all(chat.clear_domain_events())
        return message_to_dto(message)

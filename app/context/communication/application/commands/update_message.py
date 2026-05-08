"""Команда редактирования сообщения."""

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
    NotMessageAuthorException,
)
from app.context.communication.domain.exceptions.message_exceptions import (
    MessageNotFoundException,
)
from app.context.communication.domain.repositories.message_repository import (
    MessageRepository,
)


class UpdateMessageCommand(BaseCommand):
    """Отредактировать сообщение (только автор)."""

    caller_id: str
    message_id: str
    content: str | None = None
    content_format: str = "markdown"


class UpdateMessageHandler(BaseCommandHandler[UpdateMessageCommand, MessageDTO]):
    def __init__(
        self,
        message_repo: MessageRepository,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._repo = message_repo
        self._event_bus = event_bus

    async def handle(self, command: UpdateMessageCommand) -> MessageDTO:
        message = await self._repo.get_by_id(Id.from_string(command.message_id))
        if message is None:
            raise MessageNotFoundException(command.message_id)

        if str(message.sender_id) != command.caller_id:
            raise NotMessageAuthorException()

        content: RichText | None = None
        if command.content is not None:
            content = RichText(
                content=command.content,
                format=RichTextFormat(command.content_format),
            )

        message.update(content=content)
        await self._repo.update(message)
        await self._event_bus.publish_all(message.clear_domain_events())
        return message_to_dto(message)

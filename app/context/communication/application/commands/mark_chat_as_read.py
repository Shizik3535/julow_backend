"""Команда отметить чат как прочитанный."""

from __future__ import annotations

from datetime import datetime, timezone

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id

from app.context.communication.domain.exceptions.chat_exceptions import (
    ChatNotFoundException,
)
from app.context.communication.domain.repositories.chat_repository import (
    ChatRepository,
)


class MarkChatAsReadCommand(BaseCommand):
    """Отметить чат как прочитанный для caller_id."""

    caller_id: str
    chat_id: str
    read_at: datetime | None = None


class MarkChatAsReadHandler(BaseCommandHandler[MarkChatAsReadCommand, None]):
    def __init__(self, chat_repo: ChatRepository, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._repo = chat_repo
        self._event_bus = event_bus

    async def handle(self, command: MarkChatAsReadCommand) -> None:
        chat = await self._repo.get_by_id(Id.from_string(command.chat_id))
        if chat is None:
            raise ChatNotFoundException(command.chat_id)

        chat.mark_as_read(
            user_id=Id.from_string(command.caller_id),
            read_at=command.read_at or datetime.now(tz=timezone.utc),
        )
        await self._repo.update(chat)
        await self._event_bus.publish_all(chat.clear_domain_events())

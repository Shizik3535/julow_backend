"""Команды управления тредами в чате."""

from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id

from app.context.communication.application.dto.chat_dto import ThreadDTO
from app.context.communication.application.dto.mappers import thread_to_dto
from app.context.communication.domain.exceptions.chat_exceptions import (
    ChatNotFoundException,
    NotChatMemberException,
)
from app.context.communication.domain.repositories.chat_repository import (
    ChatRepository,
)


def _require_member(chat, caller_id: str) -> None:
    if not any(str(m.user_id) == caller_id for m in chat.members):
        raise NotChatMemberException()


class CreateThreadCommand(BaseCommand):
    """Создать тред в чате."""

    caller_id: str
    chat_id: str
    parent_message_id: str
    title: str | None = None


class CreateThreadHandler(BaseCommandHandler[CreateThreadCommand, ThreadDTO]):
    def __init__(self, chat_repo: ChatRepository, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._repo = chat_repo
        self._event_bus = event_bus

    async def handle(self, command: CreateThreadCommand) -> ThreadDTO:
        chat = await self._repo.get_by_id(Id.from_string(command.chat_id))
        if chat is None:
            raise ChatNotFoundException(command.chat_id)
        _require_member(chat, command.caller_id)
        thread = chat.create_thread(
            parent_message_id=Id.from_string(command.parent_message_id),
            title=command.title,
        )
        await self._repo.update(chat)
        await self._event_bus.publish_all(chat.clear_domain_events())
        return thread_to_dto(thread)


class ResolveThreadCommand(BaseCommand):
    """Закрыть тред."""

    caller_id: str
    chat_id: str
    thread_id: str


class ResolveThreadHandler(BaseCommandHandler[ResolveThreadCommand, None]):
    def __init__(self, chat_repo: ChatRepository, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._repo = chat_repo
        self._event_bus = event_bus

    async def handle(self, command: ResolveThreadCommand) -> None:
        chat = await self._repo.get_by_id(Id.from_string(command.chat_id))
        if chat is None:
            raise ChatNotFoundException(command.chat_id)
        _require_member(chat, command.caller_id)
        chat.resolve_thread(Id.from_string(command.thread_id))
        await self._repo.update(chat)
        await self._event_bus.publish_all(chat.clear_domain_events())


class ReopenThreadCommand(BaseCommand):
    """Открыть тред заново."""

    caller_id: str
    chat_id: str
    thread_id: str


class ReopenThreadHandler(BaseCommandHandler[ReopenThreadCommand, None]):
    def __init__(self, chat_repo: ChatRepository, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._repo = chat_repo
        self._event_bus = event_bus

    async def handle(self, command: ReopenThreadCommand) -> None:
        chat = await self._repo.get_by_id(Id.from_string(command.chat_id))
        if chat is None:
            raise ChatNotFoundException(command.chat_id)
        _require_member(chat, command.caller_id)
        chat.reopen_thread(Id.from_string(command.thread_id))
        await self._repo.update(chat)
        await self._event_bus.publish_all(chat.clear_domain_events())

"""Команды создания чатов: DM, групповой, канал, канал объявлений."""

from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id

from app.context.communication.application.dto.chat_dto import ChatDTO
from app.context.communication.application.dto.mappers import chat_to_dto
from app.context.communication.domain.aggregates.chat import Chat
from app.context.communication.domain.exceptions.chat_exceptions import (
    ChatAlreadyExistsException,
)
from app.context.communication.domain.repositories.chat_repository import (
    ChatRepository,
)


# ---------------------------------------------------------------------------
# DM
# ---------------------------------------------------------------------------


class CreateDMCommand(BaseCommand):
    """Создать или вернуть существующий DM между двумя пользователями."""

    caller_id: str
    other_user_id: str


class CreateDMHandler(BaseCommandHandler[CreateDMCommand, ChatDTO]):
    """Обработчик создания DM. Идемпотентен: возвращает существующий DM, если есть."""

    def __init__(self, chat_repo: ChatRepository, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._repo = chat_repo
        self._event_bus = event_bus

    async def handle(self, command: CreateDMCommand) -> ChatDTO:
        a = Id.from_string(command.caller_id)
        b = Id.from_string(command.other_user_id)
        existing = await self._repo.get_dm_between(a, b)
        if existing is not None:
            return chat_to_dto(existing)

        chat = Chat.create_dm(a, b)
        await self._repo.add(chat)
        await self._event_bus.publish_all(chat.clear_domain_events())
        return chat_to_dto(chat)


# ---------------------------------------------------------------------------
# Group
# ---------------------------------------------------------------------------


class CreateGroupChatCommand(BaseCommand):
    """Создать групповой чат."""

    caller_id: str
    name: str


class CreateGroupChatHandler(BaseCommandHandler[CreateGroupChatCommand, ChatDTO]):
    """Обработчик создания группового чата."""

    def __init__(self, chat_repo: ChatRepository, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._repo = chat_repo
        self._event_bus = event_bus

    async def handle(self, command: CreateGroupChatCommand) -> ChatDTO:
        chat = Chat.create_group(
            name=command.name,
            creator_id=Id.from_string(command.caller_id),
        )
        await self._repo.add(chat)
        await self._event_bus.publish_all(chat.clear_domain_events())
        return chat_to_dto(chat)


# ---------------------------------------------------------------------------
# Channel / Announcement
# ---------------------------------------------------------------------------


class CreateChannelCommand(BaseCommand):
    """Создать публичный канал в workspace."""

    caller_id: str
    name: str
    workspace_id: str


class CreateChannelHandler(BaseCommandHandler[CreateChannelCommand, ChatDTO]):
    """Обработчик создания канала."""

    def __init__(self, chat_repo: ChatRepository, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._repo = chat_repo
        self._event_bus = event_bus

    async def handle(self, command: CreateChannelCommand) -> ChatDTO:
        chat = Chat.create_channel(
            name=command.name,
            workspace_id=Id.from_string(command.workspace_id),
            creator_id=Id.from_string(command.caller_id),
        )
        await self._repo.add(chat)
        await self._event_bus.publish_all(chat.clear_domain_events())
        return chat_to_dto(chat)


class CreateAnnouncementCommand(BaseCommand):
    """Создать канал объявлений в workspace."""

    caller_id: str
    name: str
    workspace_id: str


class CreateAnnouncementHandler(
    BaseCommandHandler[CreateAnnouncementCommand, ChatDTO]
):
    """Обработчик создания канала объявлений."""

    def __init__(self, chat_repo: ChatRepository, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._repo = chat_repo
        self._event_bus = event_bus

    async def handle(self, command: CreateAnnouncementCommand) -> ChatDTO:
        chat = Chat.create_announcement(
            name=command.name,
            workspace_id=Id.from_string(command.workspace_id),
            creator_id=Id.from_string(command.caller_id),
        )
        await self._repo.add(chat)
        await self._event_bus.publish_all(chat.clear_domain_events())
        return chat_to_dto(chat)


__all__ = [
    "CreateDMCommand",
    "CreateDMHandler",
    "CreateGroupChatCommand",
    "CreateGroupChatHandler",
    "CreateChannelCommand",
    "CreateChannelHandler",
    "CreateAnnouncementCommand",
    "CreateAnnouncementHandler",
    "ChatAlreadyExistsException",
]

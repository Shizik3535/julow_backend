"""Команды архивирования и восстановления чата."""

from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id

from app.context.communication.application.exceptions.authorization_exceptions import (
    InsufficientChatPermissionsException,
)
from app.context.communication.domain.exceptions.chat_exceptions import (
    ChatNotFoundException,
    NotChatMemberException,
)
from app.context.communication.domain.repositories.chat_repository import (
    ChatRepository,
)
from app.context.communication.domain.value_objects.chat_member_role import (
    ChatMemberRole,
)


def _require_owner(chat, caller_id: str) -> None:
    member = next(
        (m for m in chat.members if str(m.user_id) == caller_id),
        None,
    )
    if member is None:
        raise NotChatMemberException()
    if member.role != ChatMemberRole.OWNER:
        raise InsufficientChatPermissionsException(
            chat_id=str(chat.id),
            required_roles=[ChatMemberRole.OWNER.value],
        )


class ArchiveChatCommand(BaseCommand):
    """Архивировать чат (только OWNER)."""

    caller_id: str
    chat_id: str


class ArchiveChatHandler(BaseCommandHandler[ArchiveChatCommand, None]):
    def __init__(self, chat_repo: ChatRepository, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._repo = chat_repo
        self._event_bus = event_bus

    async def handle(self, command: ArchiveChatCommand) -> None:
        chat = await self._repo.get_by_id(Id.from_string(command.chat_id))
        if chat is None:
            raise ChatNotFoundException(command.chat_id)
        _require_owner(chat, command.caller_id)
        chat.archive()
        await self._repo.update(chat)
        await self._event_bus.publish_all(chat.clear_domain_events())


class RestoreChatCommand(BaseCommand):
    """Восстановить архивированный чат (только OWNER)."""

    caller_id: str
    chat_id: str


class RestoreChatHandler(BaseCommandHandler[RestoreChatCommand, None]):
    def __init__(self, chat_repo: ChatRepository, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._repo = chat_repo
        self._event_bus = event_bus

    async def handle(self, command: RestoreChatCommand) -> None:
        chat = await self._repo.get_by_id(Id.from_string(command.chat_id))
        if chat is None:
            raise ChatNotFoundException(command.chat_id)
        _require_owner(chat, command.caller_id)
        chat.restore()
        await self._repo.update(chat)
        await self._event_bus.publish_all(chat.clear_domain_events())

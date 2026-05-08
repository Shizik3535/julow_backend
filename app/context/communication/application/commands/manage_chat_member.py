"""Команды управления участниками чата."""

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


_ADMIN_ROLES = {ChatMemberRole.OWNER, ChatMemberRole.ADMIN}
_OWNER_ONLY = {ChatMemberRole.OWNER}


def _require_role(chat, caller_id: str, allowed: set[ChatMemberRole]) -> None:
    member = next(
        (m for m in chat.members if str(m.user_id) == caller_id),
        None,
    )
    if member is None:
        raise NotChatMemberException()
    if member.role not in allowed:
        raise InsufficientChatPermissionsException(
            chat_id=str(chat.id),
            required_roles=[r.value for r in allowed],
        )


class AddChatMemberCommand(BaseCommand):
    """Добавить участника в чат (только OWNER/ADMIN)."""

    caller_id: str
    chat_id: str
    user_id: str


class AddChatMemberHandler(BaseCommandHandler[AddChatMemberCommand, None]):
    def __init__(self, chat_repo: ChatRepository, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._repo = chat_repo
        self._event_bus = event_bus

    async def handle(self, command: AddChatMemberCommand) -> None:
        chat = await self._repo.get_by_id(Id.from_string(command.chat_id))
        if chat is None:
            raise ChatNotFoundException(command.chat_id)
        _require_role(chat, command.caller_id, _ADMIN_ROLES)
        chat.add_member(Id.from_string(command.user_id))
        await self._repo.update(chat)
        await self._event_bus.publish_all(chat.clear_domain_events())


class RemoveChatMemberCommand(BaseCommand):
    """Удалить участника из чата.

    Допустимо: OWNER/ADMIN снимает любого; либо пользователь сам выходит.
    """

    caller_id: str
    chat_id: str
    user_id: str


class RemoveChatMemberHandler(BaseCommandHandler[RemoveChatMemberCommand, None]):
    def __init__(self, chat_repo: ChatRepository, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._repo = chat_repo
        self._event_bus = event_bus

    async def handle(self, command: RemoveChatMemberCommand) -> None:
        chat = await self._repo.get_by_id(Id.from_string(command.chat_id))
        if chat is None:
            raise ChatNotFoundException(command.chat_id)

        is_self_leave = command.caller_id == command.user_id
        if not is_self_leave:
            _require_role(chat, command.caller_id, _ADMIN_ROLES)

        chat.remove_member(Id.from_string(command.user_id))
        await self._repo.update(chat)
        await self._event_bus.publish_all(chat.clear_domain_events())


class ChangeChatMemberRoleCommand(BaseCommand):
    """Изменить роль участника чата (только OWNER)."""

    caller_id: str
    chat_id: str
    user_id: str
    new_role: str


class ChangeChatMemberRoleHandler(
    BaseCommandHandler[ChangeChatMemberRoleCommand, None]
):
    def __init__(self, chat_repo: ChatRepository, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._repo = chat_repo
        self._event_bus = event_bus

    async def handle(self, command: ChangeChatMemberRoleCommand) -> None:
        chat = await self._repo.get_by_id(Id.from_string(command.chat_id))
        if chat is None:
            raise ChatNotFoundException(command.chat_id)
        _require_role(chat, command.caller_id, _OWNER_ONLY)
        chat.change_member_role(
            user_id=Id.from_string(command.user_id),
            new_role=ChatMemberRole(command.new_role),
        )
        await self._repo.update(chat)
        await self._event_bus.publish_all(chat.clear_domain_events())

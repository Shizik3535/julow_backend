"""Команда обновления информации о чате."""

from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.color_vo import Color
from app.shared.domain.value_objects.id_vo import Id

from app.context.communication.application.dto.chat_dto import ChatDTO
from app.context.communication.application.dto.mappers import chat_to_dto
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


class UpdateChatInfoCommand(BaseCommand):
    """Обновить название/описание/иконку/цвет чата."""

    caller_id: str
    chat_id: str
    name: str | None = None
    description: str | None = None
    icon: str | None = None
    color: str | None = None


class UpdateChatInfoHandler(BaseCommandHandler[UpdateChatInfoCommand, ChatDTO]):
    """Обработчик обновления информации о чате (только OWNER/ADMIN)."""

    def __init__(self, chat_repo: ChatRepository, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._repo = chat_repo
        self._event_bus = event_bus

    async def handle(self, command: UpdateChatInfoCommand) -> ChatDTO:
        chat = await self._repo.get_by_id(Id.from_string(command.chat_id))
        if chat is None:
            raise ChatNotFoundException(command.chat_id)

        member = next(
            (m for m in chat.members if str(m.user_id) == command.caller_id),
            None,
        )
        if member is None:
            raise NotChatMemberException()
        if member.role not in _ADMIN_ROLES:
            raise InsufficientChatPermissionsException(
                chat_id=command.chat_id,
                required_roles=[r.value for r in _ADMIN_ROLES],
            )

        chat.update_info(
            name=command.name,
            description=command.description,
            icon=command.icon,
            color=Color(value=command.color) if command.color else None,
        )
        await self._repo.update(chat)
        await self._event_bus.publish_all(chat.clear_domain_events())
        return chat_to_dto(chat)

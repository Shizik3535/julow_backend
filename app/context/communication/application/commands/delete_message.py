"""Команда удаления сообщения (soft delete)."""

from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id

from app.context.communication.application.exceptions.authorization_exceptions import (
    InsufficientChatPermissionsException,
    NotMessageAuthorException,
)
from app.context.communication.domain.exceptions.chat_exceptions import (
    ChatNotFoundException,
)
from app.context.communication.domain.exceptions.message_exceptions import (
    MessageNotFoundException,
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


_ADMIN_ROLES = {ChatMemberRole.OWNER, ChatMemberRole.ADMIN}


class DeleteMessageCommand(BaseCommand):
    """
    Soft-delete сообщения.

    Допускается: автор сообщения либо OWNER/ADMIN чата.
    """

    caller_id: str
    message_id: str


class DeleteMessageHandler(BaseCommandHandler[DeleteMessageCommand, None]):
    def __init__(
        self,
        message_repo: MessageRepository,
        chat_repo: ChatRepository,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._repo = message_repo
        self._chat_repo = chat_repo
        self._event_bus = event_bus

    async def handle(self, command: DeleteMessageCommand) -> None:
        message = await self._repo.get_by_id(Id.from_string(command.message_id))
        if message is None:
            raise MessageNotFoundException(command.message_id)

        if str(message.sender_id) != command.caller_id:
            chat = await self._chat_repo.get_by_id(message.chat_id)
            if chat is None:
                raise ChatNotFoundException(message.chat_id)
            member = next(
                (m for m in chat.members if str(m.user_id) == command.caller_id),
                None,
            )
            if member is None or member.role not in _ADMIN_ROLES:
                raise NotMessageAuthorException()

        message.delete()
        await self._repo.update(message)
        await self._event_bus.publish_all(message.clear_domain_events())

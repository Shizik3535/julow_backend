"""Команды управления реакциями на сообщения чата."""

from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id

from app.context.communication.domain.exceptions.chat_exceptions import (
    ChatNotFoundException,
    NotChatMemberException,
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
from app.context.communication.domain.value_objects.reaction_emoji import ReactionEmoji


async def _ensure_chat_member(
    chat_repo: ChatRepository, chat_id: Id, user_id: str
) -> None:
    chat = await chat_repo.get_by_id(chat_id)
    if chat is None:
        raise ChatNotFoundException(chat_id)
    if not any(str(m.user_id) == user_id for m in chat.members):
        raise NotChatMemberException()


class AddMessageReactionCommand(BaseCommand):
    """Добавить реакцию на сообщение."""

    caller_id: str
    message_id: str
    emoji: str


class AddMessageReactionHandler(
    BaseCommandHandler[AddMessageReactionCommand, None]
):
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

    async def handle(self, command: AddMessageReactionCommand) -> None:
        message = await self._repo.get_by_id(Id.from_string(command.message_id))
        if message is None:
            raise MessageNotFoundException(command.message_id)
        await _ensure_chat_member(self._chat_repo, message.chat_id, command.caller_id)

        message.add_reaction(
            user_id=Id.from_string(command.caller_id),
            emoji=ReactionEmoji(value=command.emoji),
        )
        await self._repo.update(message)
        await self._event_bus.publish_all(message.clear_domain_events())


class RemoveMessageReactionCommand(BaseCommand):
    """Снять реакцию с сообщения."""

    caller_id: str
    message_id: str
    emoji: str


class RemoveMessageReactionHandler(
    BaseCommandHandler[RemoveMessageReactionCommand, None]
):
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

    async def handle(self, command: RemoveMessageReactionCommand) -> None:
        message = await self._repo.get_by_id(Id.from_string(command.message_id))
        if message is None:
            raise MessageNotFoundException(command.message_id)
        await _ensure_chat_member(self._chat_repo, message.chat_id, command.caller_id)

        message.remove_reaction(
            user_id=Id.from_string(command.caller_id),
            emoji=ReactionEmoji(value=command.emoji),
        )
        await self._repo.update(message)
        await self._event_bus.publish_all(message.clear_domain_events())

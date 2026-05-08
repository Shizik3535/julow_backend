from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id

from app.context.communication.application.ports.integration.inboard.comment_target_access_port import (
    CommentTargetAccessPort,
)
from app.context.communication.domain.exceptions.comment_exceptions import (
    CommentNotFoundException,
)
from app.context.communication.domain.repositories.comment_repository import (
    CommentRepository,
)
from app.context.communication.domain.value_objects.reaction_emoji import ReactionEmoji


class AddCommentReactionCommand(BaseCommand):
    """
    Команда добавления реакции на комментарий.

    Атрибуты:
        comment_id: ID комментария.
        user_id: ID пользователя, ставящего реакцию.
        emoji: Unicode emoji.
    """

    comment_id: str
    user_id: str
    emoji: str


class AddCommentReactionHandler(BaseCommandHandler[AddCommentReactionCommand, None]):
    """Обработчик добавления реакции на комментарий."""

    def __init__(
        self,
        comment_repo: CommentRepository,
        target_access: CommentTargetAccessPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._repo = comment_repo
        self._target_access = target_access
        self._event_bus = event_bus

    async def handle(self, command: AddCommentReactionCommand) -> None:
        comment = await self._repo.get_by_id(Id.from_string(command.comment_id))
        if comment is None:
            raise CommentNotFoundException(command.comment_id)

        await self._target_access.require_access(
            user_id=command.user_id,
            target_type=comment.target_type,
            target_id=str(comment.target_id),
        )

        comment.add_reaction(
            user_id=Id.from_string(command.user_id),
            emoji=ReactionEmoji(value=command.emoji),
        )
        await self._repo.update(comment)
        await self._event_bus.publish_all(comment.clear_domain_events())


class RemoveCommentReactionCommand(BaseCommand):
    """
    Команда снятия реакции с комментария.

    Атрибуты:
        comment_id: ID комментария.
        user_id: ID пользователя.
        emoji: Unicode emoji.
    """

    comment_id: str
    user_id: str
    emoji: str


class RemoveCommentReactionHandler(
    BaseCommandHandler[RemoveCommentReactionCommand, None]
):
    """Обработчик снятия реакции с комментария."""

    def __init__(
        self,
        comment_repo: CommentRepository,
        target_access: CommentTargetAccessPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._repo = comment_repo
        self._target_access = target_access
        self._event_bus = event_bus

    async def handle(self, command: RemoveCommentReactionCommand) -> None:
        comment = await self._repo.get_by_id(Id.from_string(command.comment_id))
        if comment is None:
            raise CommentNotFoundException(command.comment_id)

        await self._target_access.require_access(
            user_id=command.user_id,
            target_type=comment.target_type,
            target_id=str(comment.target_id),
        )

        comment.remove_reaction(
            user_id=Id.from_string(command.user_id),
            emoji=ReactionEmoji(value=command.emoji),
        )
        await self._repo.update(comment)
        await self._event_bus.publish_all(comment.clear_domain_events())

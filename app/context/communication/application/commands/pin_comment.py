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


class PinCommentCommand(BaseCommand):
    """Команда закрепить комментарий."""

    comment_id: str
    caller_id: str


class PinCommentHandler(BaseCommandHandler[PinCommentCommand, None]):
    """Обработчик закрепления комментария."""

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

    async def handle(self, command: PinCommentCommand) -> None:
        comment = await self._repo.get_by_id(Id.from_string(command.comment_id))
        if comment is None:
            raise CommentNotFoundException(command.comment_id)
        await self._target_access.require_access(
            user_id=command.caller_id,
            target_type=comment.target_type,
            target_id=str(comment.target_id),
        )
        comment.pin()
        await self._repo.update(comment)
        await self._event_bus.publish_all(comment.clear_domain_events())


class UnpinCommentCommand(BaseCommand):
    """Команда открепить комментарий."""

    comment_id: str
    caller_id: str


class UnpinCommentHandler(BaseCommandHandler[UnpinCommentCommand, None]):
    """Обработчик открепления комментария."""

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

    async def handle(self, command: UnpinCommentCommand) -> None:
        comment = await self._repo.get_by_id(Id.from_string(command.comment_id))
        if comment is None:
            raise CommentNotFoundException(command.comment_id)
        await self._target_access.require_access(
            user_id=command.caller_id,
            target_type=comment.target_type,
            target_id=str(comment.target_id),
        )
        comment.unpin()
        await self._repo.update(comment)
        await self._event_bus.publish_all(comment.clear_domain_events())

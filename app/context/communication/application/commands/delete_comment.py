from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id

from app.context.communication.domain.exceptions.comment_exceptions import (
    CommentNotFoundException,
    NotCommentAuthorException,
)
from app.context.communication.domain.repositories.comment_repository import (
    CommentRepository,
)


class DeleteCommentCommand(BaseCommand):
    """
    Команда удаления (soft) комментария.

    Атрибуты:
        comment_id: ID комментария.
        caller_id: ID пользователя, инициирующего удаление (только автор).
    """

    comment_id: str
    caller_id: str


class DeleteCommentHandler(BaseCommandHandler[DeleteCommentCommand, None]):
    """Обработчик soft delete комментария."""

    def __init__(
        self,
        comment_repo: CommentRepository,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._repo = comment_repo
        self._event_bus = event_bus

    async def handle(self, command: DeleteCommentCommand) -> None:
        comment = await self._repo.get_by_id(Id.from_string(command.comment_id))
        if comment is None:
            raise CommentNotFoundException(command.comment_id)

        if str(comment.author_id) != command.caller_id:
            raise NotCommentAuthorException()

        comment.delete()
        await self._repo.update(comment)
        await self._event_bus.publish_all(comment.clear_domain_events())

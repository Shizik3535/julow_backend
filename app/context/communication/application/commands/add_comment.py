from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.rich_text_format import RichTextFormat
from app.shared.domain.value_objects.rich_text_vo import RichText

from app.context.communication.application.dto.comment_dto import CommentDTO
from app.context.communication.application.dto.mappers import comment_to_dto
from app.context.communication.application.ports.integration.inboard.comment_target_access_port import (
    CommentTargetAccessPort,
)
from app.context.communication.domain.aggregates.comment import Comment
from app.context.communication.domain.exceptions.comment_exceptions import (
    CommentNotFoundException,
)
from app.context.communication.domain.repositories.comment_repository import (
    CommentRepository,
)
from app.context.communication.domain.value_objects.comment_target_type import (
    CommentTargetType,
)


class AddCommentCommand(BaseCommand):
    """
    Команда добавления комментария.

    Атрибуты:
        author_id: ID автора (UUID).
        target_type: Тип комментируемой сущности (task/project/...).
        target_id: ID комментируемой сущности (UUID).
        content: Текст комментария.
        content_format: Формат содержимого (markdown/wysiwyg).
        parent_comment_id: ID родительского комментария (для ответов).
    """

    author_id: str
    target_type: str
    target_id: str
    content: str | None = None
    content_format: str = "markdown"
    parent_comment_id: str | None = None


class AddCommentHandler(BaseCommandHandler[AddCommentCommand, CommentDTO]):
    """Обработчик добавления комментария."""

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

    async def handle(self, command: AddCommentCommand) -> CommentDTO:
        target_type = CommentTargetType(command.target_type)
        target_id = Id.from_string(command.target_id)
        author_id = Id.from_string(command.author_id)

        await self._target_access.require_access(
            user_id=command.author_id,
            target_type=target_type,
            target_id=command.target_id,
        )

        content: RichText | None = None
        if command.content is not None:
            content = RichText(
                content=command.content,
                format=RichTextFormat(command.content_format),
            )

        parent_comment_id: Id | None = None
        if command.parent_comment_id:
            parent_comment_id = Id.from_string(command.parent_comment_id)
            parent = await self._repo.get_by_id(parent_comment_id)
            if parent is None:
                raise CommentNotFoundException(command.parent_comment_id)

        comment = Comment.create(
            author_id=author_id,
            target_type=target_type,
            target_id=target_id,
            content=content,
            parent_comment_id=parent_comment_id,
        )

        await self._repo.add(comment)
        await self._event_bus.publish_all(comment.clear_domain_events())

        return comment_to_dto(comment)

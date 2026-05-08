from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id

from app.context.communication.application.dto.comment_dto import CommentDTO
from app.context.communication.application.dto.mappers import comment_to_dto
from app.context.communication.application.ports.integration.inboard.comment_target_access_port import (
    CommentTargetAccessPort,
)
from app.context.communication.domain.exceptions.comment_exceptions import (
    CommentNotFoundException,
)
from app.context.communication.domain.repositories.comment_repository import (
    CommentRepository,
)


class GetCommentQuery(BaseQuery):
    """Запрос комментария по ID."""

    comment_id: str
    caller_id: str


class GetCommentHandler(BaseQueryHandler[GetCommentQuery, CommentDTO]):
    """Обработчик запроса комментария."""

    def __init__(
        self,
        comment_repo: CommentRepository,
        target_access: CommentTargetAccessPort,
    ) -> None:
        super().__init__()
        self._repo = comment_repo
        self._target_access = target_access

    async def handle(self, query: GetCommentQuery) -> CommentDTO:
        comment = await self._repo.get_by_id(Id.from_string(query.comment_id))
        if comment is None:
            raise CommentNotFoundException(query.comment_id)
        await self._target_access.require_access(
            user_id=query.caller_id,
            target_type=comment.target_type,
            target_id=str(comment.target_id),
        )
        return comment_to_dto(comment)

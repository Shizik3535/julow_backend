from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id

from app.context.communication.application.dto.comment_dto import CommentListDTO
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


class GetCommentRepliesQuery(BaseQuery):
    """Запрос ответов на комментарий."""

    comment_id: str
    caller_id: str
    include_deleted: bool = False


class GetCommentRepliesHandler(
    BaseQueryHandler[GetCommentRepliesQuery, CommentListDTO]
):
    """Обработчик запроса ответов на комментарий."""

    def __init__(
        self,
        comment_repo: CommentRepository,
        target_access: CommentTargetAccessPort,
    ) -> None:
        super().__init__()
        self._repo = comment_repo
        self._target_access = target_access

    async def handle(self, query: GetCommentRepliesQuery) -> CommentListDTO:
        parent = await self._repo.get_by_id(Id.from_string(query.comment_id))
        if parent is None:
            raise CommentNotFoundException(query.comment_id)

        await self._target_access.require_access(
            user_id=query.caller_id,
            target_type=parent.target_type,
            target_id=str(parent.target_id),
        )

        replies = await self._repo.get_replies(Id.from_string(query.comment_id))
        if not query.include_deleted:
            replies = [r for r in replies if not r.is_deleted]
        items = [comment_to_dto(r) for r in replies]
        return CommentListDTO(items=items, total=len(items))

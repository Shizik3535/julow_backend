from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id

from app.context.communication.application.dto.comment_dto import CommentListDTO
from app.context.communication.application.dto.mappers import comment_to_dto
from app.context.communication.application.ports.integration.inboard.comment_target_access_port import (
    CommentTargetAccessPort,
)
from app.context.communication.domain.repositories.comment_repository import (
    CommentRepository,
)
from app.context.communication.domain.value_objects.comment_target_type import (
    CommentTargetType,
)


class GetCommentsByTargetQuery(BaseQuery):
    """
    Запрос комментариев по комментируемой сущности.

    Атрибуты:
        target_type: Тип сущности.
        target_id: ID сущности.
        caller_id: Идентификатор вызывающего пользователя (для проверки доступа).
        include_deleted: Включать ли soft-deleted.
        only_root: Только корневые (без родителя).
    """

    target_type: str
    target_id: str
    caller_id: str
    include_deleted: bool = False
    only_root: bool = False


class GetCommentsByTargetHandler(
    BaseQueryHandler[GetCommentsByTargetQuery, CommentListDTO]
):
    """Обработчик запроса комментариев по target."""

    def __init__(
        self,
        comment_repo: CommentRepository,
        target_access: CommentTargetAccessPort,
    ) -> None:
        super().__init__()
        self._repo = comment_repo
        self._target_access = target_access

    async def handle(self, query: GetCommentsByTargetQuery) -> CommentListDTO:
        target_type = CommentTargetType(query.target_type)
        target_id = Id.from_string(query.target_id)

        await self._target_access.require_access(
            user_id=query.caller_id,
            target_type=target_type,
            target_id=query.target_id,
        )

        comments = await self._repo.get_by_target_and_type(target_id, target_type)

        if not query.include_deleted:
            comments = [c for c in comments if not c.is_deleted]
        if query.only_root:
            comments = [c for c in comments if c.parent_comment_id is None]

        items = [comment_to_dto(c) for c in comments]
        return CommentListDTO(items=items, total=len(items))

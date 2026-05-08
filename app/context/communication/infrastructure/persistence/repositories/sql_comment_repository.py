from __future__ import annotations

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.domain.exceptions.entity_not_found_exception import (
    EntityNotFoundException,
)
from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.persistence.sqlalchemy_repository import (
    SqlAlchemyRepository,
)

from app.context.communication.domain.aggregates.comment import Comment
from app.context.communication.domain.repositories.comment_repository import (
    CommentRepository,
)
from app.context.communication.domain.value_objects.comment_target_type import (
    CommentTargetType,
)
from app.context.communication.infrastructure.persistence.mappers.comment_mapper import (
    CommentMapper,
)
from app.context.communication.infrastructure.persistence.orm_models.comment_orm import (
    CommentAttachmentORM,
    CommentORM,
    CommentReactionORM,
)


class SqlCommentRepository(
    SqlAlchemyRepository[Comment, CommentORM],
    CommentRepository,
):
    """SQLAlchemy-реализация CommentRepository."""

    def __init__(self, session: AsyncSession, mapper: CommentMapper) -> None:
        super().__init__(session=session, mapper=mapper, orm_model_class=CommentORM)
        self._mapper: CommentMapper = mapper

    async def update(self, aggregate: Comment) -> Comment:
        """
        Обновить комментарий вместе с дочерними коллекциями
        (reactions, attachments).

        Перезаписывает дочерние коллекции полностью для упрощения
        синхронизации между доменом и хранилищем.
        """
        uuid_value = self._mapper._map_uuid(aggregate.id)
        stmt = select(CommentORM).where(CommentORM.id == uuid_value)
        result = await self._session.execute(stmt)
        orm_model = result.scalar_one_or_none()
        if orm_model is None:
            raise EntityNotFoundException(entity_type="Comment", id=aggregate.id)

        # Скалярные поля
        orm_model.author_id = self._mapper._map_uuid(aggregate.author_id)
        orm_model.target_type = aggregate.target_type.value
        orm_model.target_id = self._mapper._map_uuid(aggregate.target_id)
        orm_model.parent_comment_id = (
            self._mapper._map_uuid(aggregate.parent_comment_id)
            if aggregate.parent_comment_id
            else None
        )
        orm_model.content = aggregate.content.content if aggregate.content else None
        orm_model.content_format = (
            aggregate.content.format.value if aggregate.content else "markdown"
        )
        orm_model.is_pinned = aggregate.is_pinned
        orm_model.is_system = aggregate.is_system
        orm_model.is_deleted = aggregate.is_deleted
        orm_model.updated_at = aggregate.updated_at

        # Реакции — заменяем коллекцию (cascade delete-orphan удалит старые)
        orm_model.reactions = [
            self._mapper._reaction_to_orm(r, aggregate.id) for r in aggregate.reactions
        ]
        orm_model.attachments = [
            self._mapper._attachment_to_orm(a, aggregate.id)
            for a in aggregate.attachments
        ]

        await self._session.flush()
        return aggregate

    # ------------------------------------------------------------------
    # CommentRepository — query-методы
    # ------------------------------------------------------------------

    async def get_by_target(self, target_id: Id) -> list[Comment]:
        target_uuid = self._mapper._map_uuid(target_id)
        stmt = (
            select(CommentORM)
            .where(CommentORM.target_id == target_uuid)
            .order_by(CommentORM.created_at.asc())
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(orm) for orm in result.scalars().all()]

    async def get_by_target_and_type(
        self, target_id: Id, target_type: CommentTargetType
    ) -> list[Comment]:
        target_uuid = self._mapper._map_uuid(target_id)
        stmt = (
            select(CommentORM)
            .where(
                CommentORM.target_id == target_uuid,
                CommentORM.target_type == target_type.value,
            )
            .order_by(CommentORM.created_at.asc())
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(orm) for orm in result.scalars().all()]

    async def get_replies(self, parent_comment_id: Id) -> list[Comment]:
        parent_uuid = self._mapper._map_uuid(parent_comment_id)
        stmt = (
            select(CommentORM)
            .where(CommentORM.parent_comment_id == parent_uuid)
            .order_by(CommentORM.created_at.asc())
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(orm) for orm in result.scalars().all()]

    async def get_by_author(self, author_id: Id) -> list[Comment]:
        author_uuid = self._mapper._map_uuid(author_id)
        stmt = (
            select(CommentORM)
            .where(CommentORM.author_id == author_uuid)
            .order_by(CommentORM.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(orm) for orm in result.scalars().all()]

    async def search(
        self,
        offset: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
    ) -> list[Comment]:
        stmt = select(CommentORM)
        if filters:
            for field_name, value in filters.items():
                col = getattr(CommentORM, field_name, None)
                if col is not None:
                    stmt = stmt.where(col == value)
        stmt = stmt.order_by(CommentORM.created_at.desc()).offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(orm) for orm in result.scalars().all()]

    async def count_by_target(self, target_id: Id) -> int:
        target_uuid = self._mapper._map_uuid(target_id)
        stmt = (
            select(func.count())
            .select_from(CommentORM)
            .where(
                CommentORM.target_id == target_uuid,
                CommentORM.is_deleted == False,  # noqa: E712
            )
        )
        result = await self._session.execute(stmt)
        return int(result.scalar_one())

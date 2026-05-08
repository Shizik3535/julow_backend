from __future__ import annotations

from datetime import datetime
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

from app.context.communication.domain.aggregates.message import Message
from app.context.communication.domain.repositories.message_repository import (
    MessageRepository,
)
from app.context.communication.infrastructure.persistence.mappers.message_mapper import (
    MessageMapper,
)
from app.context.communication.infrastructure.persistence.orm_models.message_orm import (
    MessageORM,
)


class SqlMessageRepository(
    SqlAlchemyRepository[Message, MessageORM],
    MessageRepository,
):
    """SQLAlchemy-реализация MessageRepository."""

    def __init__(self, session: AsyncSession, mapper: MessageMapper) -> None:
        super().__init__(session=session, mapper=mapper, orm_model_class=MessageORM)
        self._mapper: MessageMapper = mapper

    async def update(self, aggregate: Message) -> Message:
        """Обновить сообщение вместе с дочерними коллекциями."""
        uuid_value = self._mapper._map_uuid(aggregate.id)
        stmt = select(MessageORM).where(MessageORM.id == uuid_value)
        result = await self._session.execute(stmt)
        orm_model = result.scalar_one_or_none()
        if orm_model is None:
            raise EntityNotFoundException(entity_type="Message", id=aggregate.id)

        orm_model.chat_id = self._mapper._map_uuid(aggregate.chat_id)
        orm_model.thread_id = (
            self._mapper._map_uuid(aggregate.thread_id)
            if aggregate.thread_id
            else None
        )
        orm_model.sender_id = self._mapper._map_uuid(aggregate.sender_id)
        orm_model.reply_to_id = (
            self._mapper._map_uuid(aggregate.reply_to_id)
            if aggregate.reply_to_id
            else None
        )
        orm_model.content = aggregate.content.content if aggregate.content else None
        orm_model.content_format = (
            aggregate.content.format.value if aggregate.content else "markdown"
        )
        orm_model.message_type = aggregate.message_type.value
        orm_model.is_edited = aggregate.is_edited
        orm_model.is_deleted = aggregate.is_deleted
        orm_model.updated_at = aggregate.updated_at

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
    # MessageRepository — query-методы
    # ------------------------------------------------------------------

    async def get_by_chat(
        self, chat_id: Id, offset: int = 0, limit: int = 50
    ) -> list[Message]:
        chat_uuid = self._mapper._map_uuid(chat_id)
        stmt = (
            select(MessageORM)
            .where(MessageORM.chat_id == chat_uuid)
            .order_by(MessageORM.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(orm) for orm in result.scalars().all()]

    async def get_by_thread(self, thread_id: Id) -> list[Message]:
        thread_uuid = self._mapper._map_uuid(thread_id)
        stmt = (
            select(MessageORM)
            .where(MessageORM.thread_id == thread_uuid)
            .order_by(MessageORM.created_at.asc())
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(orm) for orm in result.scalars().all()]

    async def get_by_chat_after(
        self, chat_id: Id, after: datetime
    ) -> list[Message]:
        chat_uuid = self._mapper._map_uuid(chat_id)
        stmt = (
            select(MessageORM)
            .where(
                MessageORM.chat_id == chat_uuid,
                MessageORM.created_at > after,
            )
            .order_by(MessageORM.created_at.asc())
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(orm) for orm in result.scalars().all()]

    async def search(
        self,
        offset: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
    ) -> list[Message]:
        stmt = select(MessageORM)
        if filters:
            for field_name, value in filters.items():
                col = getattr(MessageORM, field_name, None)
                if col is not None:
                    stmt = stmt.where(col == value)
        stmt = stmt.order_by(MessageORM.created_at.desc()).offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(orm) for orm in result.scalars().all()]

    async def count_unread(self, chat_id: Id, after: datetime) -> int:
        chat_uuid = self._mapper._map_uuid(chat_id)
        stmt = (
            select(func.count())
            .select_from(MessageORM)
            .where(
                MessageORM.chat_id == chat_uuid,
                MessageORM.created_at > after,
                MessageORM.is_deleted == False,  # noqa: E712
            )
        )
        result = await self._session.execute(stmt)
        return int(result.scalar_one())

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.domain.exceptions.entity_not_found_exception import (
    EntityNotFoundException,
)
from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.persistence.sqlalchemy_repository import (
    SqlAlchemyRepository,
)

from app.context.communication.domain.aggregates.chat import Chat
from app.context.communication.domain.repositories.chat_repository import (
    ChatRepository,
)
from app.context.communication.domain.value_objects.chat_type import ChatType
from app.context.communication.infrastructure.persistence.mappers.chat_mapper import (
    ChatMapper,
)
from app.context.communication.infrastructure.persistence.orm_models.chat_orm import (
    ChatMemberORM,
    ChatORM,
)


class SqlChatRepository(
    SqlAlchemyRepository[Chat, ChatORM],
    ChatRepository,
):
    """SQLAlchemy-реализация ChatRepository."""

    def __init__(self, session: AsyncSession, mapper: ChatMapper) -> None:
        super().__init__(session=session, mapper=mapper, orm_model_class=ChatORM)
        self._mapper: ChatMapper = mapper

    async def update(self, aggregate: Chat) -> Chat:
        """Обновить чат вместе с дочерними коллекциями (members, threads)."""
        uuid_value = self._mapper._map_uuid(aggregate.id)
        stmt = select(ChatORM).where(ChatORM.id == uuid_value)
        result = await self._session.execute(stmt)
        orm_model = result.scalar_one_or_none()
        if orm_model is None:
            raise EntityNotFoundException(entity_type="Chat", id=aggregate.id)

        orm_model.chat_type = aggregate.chat_type.value
        orm_model.name = aggregate.name
        orm_model.description = aggregate.description
        orm_model.icon = aggregate.icon
        orm_model.color = aggregate.color.value if aggregate.color else None
        orm_model.workspace_id = (
            self._mapper._map_uuid(aggregate.workspace_id)
            if aggregate.workspace_id
            else None
        )
        orm_model.project_id = (
            self._mapper._map_uuid(aggregate.project_id)
            if aggregate.project_id
            else None
        )
        orm_model.last_message_at = aggregate.last_message_at
        orm_model.is_archived = aggregate.is_archived
        orm_model.updated_at = aggregate.updated_at

        orm_model.members = [
            self._mapper._member_to_orm(m, aggregate.id) for m in aggregate.members
        ]
        orm_model.threads = [
            self._mapper._thread_to_orm(t, aggregate.id) for t in aggregate.threads
        ]

        await self._session.flush()
        return aggregate

    # ------------------------------------------------------------------
    # ChatRepository — query-методы
    # ------------------------------------------------------------------

    async def get_by_member(self, user_id: Id) -> list[Chat]:
        user_uuid = self._mapper._map_uuid(user_id)
        stmt = (
            select(ChatORM)
            .join(ChatMemberORM, ChatMemberORM.chat_id == ChatORM.id)
            .where(ChatMemberORM.user_id == user_uuid)
            .order_by(ChatORM.last_message_at.desc().nullslast())
        )
        result = await self._session.execute(stmt)
        chats = result.scalars().unique().all()
        return [self._mapper.to_domain(orm) for orm in chats]

    async def get_dm_between(self, user_a: Id, user_b: Id) -> Chat | None:
        a_uuid = self._mapper._map_uuid(user_a)
        b_uuid = self._mapper._map_uuid(user_b)

        members_a = (
            select(ChatMemberORM.chat_id).where(ChatMemberORM.user_id == a_uuid)
        ).subquery()
        members_b = (
            select(ChatMemberORM.chat_id).where(ChatMemberORM.user_id == b_uuid)
        ).subquery()

        stmt = (
            select(ChatORM)
            .where(
                ChatORM.chat_type == ChatType.DM.value,
                ChatORM.id.in_(select(members_a)),
                ChatORM.id.in_(select(members_b)),
            )
            .limit(1)
        )
        result = await self._session.execute(stmt)
        orm = result.scalars().first()
        return self._mapper.to_domain(orm) if orm else None

    async def get_by_workspace(self, workspace_id: Id) -> list[Chat]:
        ws_uuid = self._mapper._map_uuid(workspace_id)
        stmt = (
            select(ChatORM)
            .where(ChatORM.workspace_id == ws_uuid)
            .order_by(ChatORM.created_at.asc())
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(orm) for orm in result.scalars().all()]

    async def get_by_project_id(self, project_id: Id) -> Chat | None:
        project_uuid = self._mapper._map_uuid(project_id)
        stmt = (
            select(ChatORM)
            .where(ChatORM.project_id == project_uuid)
            .order_by(ChatORM.created_at.asc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        orm = result.scalars().first()
        return self._mapper.to_domain(orm) if orm else None

    async def get_by_type(self, chat_type: ChatType) -> list[Chat]:
        stmt = (
            select(ChatORM)
            .where(ChatORM.chat_type == chat_type.value)
            .order_by(ChatORM.created_at.asc())
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(orm) for orm in result.scalars().all()]

    async def search(
        self,
        offset: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
    ) -> list[Chat]:
        stmt = select(ChatORM)
        if filters:
            for field_name, value in filters.items():
                col = getattr(ChatORM, field_name, None)
                if col is not None:
                    stmt = stmt.where(col == value)
        stmt = stmt.order_by(ChatORM.created_at.desc()).offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(orm) for orm in result.scalars().all()]

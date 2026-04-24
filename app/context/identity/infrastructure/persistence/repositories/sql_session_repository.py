from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.persistence.sqlalchemy_repository import SqlAlchemyRepository
from app.context.identity.domain.aggregates.session import Session
from app.context.identity.domain.repositories.session_repository import SessionRepository
from app.context.identity.domain.value_objects.refresh_token import RefreshToken
from app.context.identity.infrastructure.persistence.mappers.session_mapper import SessionMapper
from app.context.identity.infrastructure.persistence.orm_models.session_orm import SessionORM


class SqlSessionRepository(SqlAlchemyRepository[Session, SessionORM], SessionRepository):
    """SQLAlchemy-реализация SessionRepository."""

    def __init__(self, session: AsyncSession, mapper: SessionMapper) -> None:
        super().__init__(session=session, mapper=mapper, orm_model_class=SessionORM)

    async def get_active_by_user(self, user_id: Id) -> list[Session]:
        uuid_val = self._mapper._map_uuid(user_id)
        stmt = select(SessionORM).where(
            SessionORM.user_id == uuid_val,
            SessionORM.status == "active",
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(o) for o in result.scalars().all()]

    async def get_by_user(
        self,
        user_id: Id,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Session]:
        uuid_val = self._mapper._map_uuid(user_id)
        stmt = (
            select(SessionORM)
            .where(SessionORM.user_id == uuid_val)
            .order_by(SessionORM.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(o) for o in result.scalars().all()]

    async def count_active_by_user(self, user_id: Id) -> int:
        uuid_val = self._mapper._map_uuid(user_id)
        stmt = (
            select(func.count())
            .select_from(SessionORM)
            .where(
                SessionORM.user_id == uuid_val,
                SessionORM.status == "active",
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def get_by_refresh_token(self, token: RefreshToken) -> Session | None:
        stmt = select(SessionORM).where(
            SessionORM.refresh_token == token.value,
            SessionORM.status == "active",
        )
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._mapper.to_domain(orm) if orm else None

    async def terminate_all_by_user(
        self,
        user_id: Id,
        except_session_id: Id | None = None,
    ) -> int:
        uuid_val = self._mapper._map_uuid(user_id)
        now = datetime.now(tz=timezone.utc)

        stmt = (
            update(SessionORM)
            .where(
                SessionORM.user_id == uuid_val,
                SessionORM.status == "active",
            )
            .values(status="terminated", terminated_at=now)
        )

        if except_session_id is not None:
            except_uuid = self._mapper._map_uuid(except_session_id)
            stmt = stmt.where(SessionORM.id != except_uuid)

        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.rowcount

    async def terminate_by_user(self, user_id: Id, session_id: Id) -> bool:
        user_uuid = self._mapper._map_uuid(user_id)
        session_uuid = self._mapper._map_uuid(session_id)
        now = datetime.now(tz=timezone.utc)

        stmt = (
            update(SessionORM)
            .where(
                SessionORM.id == session_uuid,
                SessionORM.user_id == user_uuid,
                SessionORM.status == "active",
            )
            .values(status="terminated", terminated_at=now)
        )
        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.rowcount > 0

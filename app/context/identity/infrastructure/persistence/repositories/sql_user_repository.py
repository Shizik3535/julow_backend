from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.domain.value_objects.email_vo import Email
from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.persistence.sqlalchemy_repository import SqlAlchemyRepository
from app.context.identity.domain.aggregates.user import User
from app.context.identity.domain.repositories.user_repository import UserRepository
from app.context.identity.infrastructure.persistence.mappers.user_mapper import UserMapper
from app.context.identity.infrastructure.persistence.orm_models.user_orm import UserORM, user_roles_table


class SqlUserRepository(SqlAlchemyRepository[User, UserORM], UserRepository):
    """SQLAlchemy-реализация UserRepository."""

    def __init__(self, session: AsyncSession, mapper: UserMapper) -> None:
        super().__init__(session=session, mapper=mapper, orm_model_class=UserORM)

    async def get_by_email(self, email: Email) -> User | None:
        stmt = select(UserORM).where(UserORM.email == email.value)
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._mapper.to_domain(orm) if orm else None

    async def get_by_role(self, role_id: Id) -> list[User]:
        uuid_val = self._mapper._map_uuid(role_id)
        stmt = (
            select(UserORM)
            .join(user_roles_table, UserORM.id == user_roles_table.c.user_id)
            .where(user_roles_table.c.role_id == uuid_val)
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(o) for o in result.scalars().all()]

    async def search(
        self,
        offset: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
    ) -> list[User]:
        stmt = select(UserORM)
        if filters:
            email = filters.get("email")
            if email:
                safe = email.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
                stmt = stmt.where(UserORM.email.ilike(f"%{safe}%", escape="\\"))
            status = filters.get("status")
            if status:
                stmt = stmt.where(UserORM.status == status)
        stmt = stmt.offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(o) for o in result.scalars().all()]

    async def add(self, aggregate: User) -> User:
        """Переопределяем add для синхронизации user_roles association."""
        orm_model = self._mapper.to_orm(aggregate)
        self._session.add(orm_model)
        await self._session.flush()

        # Синхронизация ролей через association table
        for role_id in aggregate.role_ids:
            uuid_val = self._mapper._map_uuid(role_id)
            await self._session.execute(
                user_roles_table.insert().values(user_id=orm_model.id, role_id=uuid_val)
            )

        await self._session.flush()
        return aggregate

    async def update(self, aggregate: User) -> User:
        """Переопределяем update для синхронизации user_roles association."""
        result = await super().update(aggregate)

        # Удаляем старые роли
        uuid_val = self._mapper._map_uuid(aggregate.id)
        await self._session.execute(
            user_roles_table.delete().where(user_roles_table.c.user_id == uuid_val)
        )

        # Вставляем актуальные роли
        for role_id in aggregate.role_ids:
            role_uuid = self._mapper._map_uuid(role_id)
            await self._session.execute(
                user_roles_table.insert().values(user_id=uuid_val, role_id=role_uuid)
            )

        await self._session.flush()
        return result

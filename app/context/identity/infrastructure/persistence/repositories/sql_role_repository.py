from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.context.identity.domain.aggregates.role import Role
from app.context.identity.domain.repositories.role_repository import RoleRepository
from app.context.identity.infrastructure.persistence.mappers.role_mapper import RoleMapper
from app.context.identity.infrastructure.persistence.orm_models.role_orm import RoleORM
from app.shared.infrastructure.persistence.sqlalchemy_repository import SqlAlchemyRepository


class SqlRoleRepository(SqlAlchemyRepository[Role, RoleORM], RoleRepository):
    """SQLAlchemy-реализация RoleRepository."""

    def __init__(self, session: AsyncSession, mapper: RoleMapper) -> None:
        super().__init__(session=session, mapper=mapper, orm_model_class=RoleORM)

    async def get_by_name(self, name: str) -> Role | None:
        stmt = select(RoleORM).where(RoleORM.name == name)
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._mapper.to_domain(orm) if orm else None

    async def get_system_roles(self) -> list[Role]:
        stmt = select(RoleORM).where(RoleORM.is_system.is_(True))
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(o) for o in result.scalars().all()]

    async def search(
        self,
        offset: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
    ) -> list[Role]:
        stmt = select(RoleORM)
        if filters:
            name = filters.get("name")
            if name:
                safe = name.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
                stmt = stmt.where(RoleORM.name.ilike(f"%{safe}%", escape="\\"))
            is_system = filters.get("is_system")
            if is_system is not None:
                stmt = stmt.where(RoleORM.is_system.is_(is_system))
        stmt = stmt.offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(o) for o in result.scalars().all()]

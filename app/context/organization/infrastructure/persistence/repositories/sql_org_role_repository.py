from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.persistence.sqlalchemy_repository import SqlAlchemyRepository
from app.context.organization.domain.aggregates.org_role import OrgRole
from app.context.organization.domain.repositories.org_role_repository import OrgRoleRepository
from app.context.organization.infrastructure.persistence.mappers.org_role_mapper import OrgRoleMapper
from app.context.organization.infrastructure.persistence.orm_models.org_role_orm import OrgRoleORM


class SqlOrgRoleRepository(SqlAlchemyRepository[OrgRole, OrgRoleORM], OrgRoleRepository):
    """SQLAlchemy-реализация OrgRoleRepository."""

    def __init__(self, session: AsyncSession, mapper: OrgRoleMapper) -> None:
        super().__init__(session=session, mapper=mapper, orm_model_class=OrgRoleORM)

    async def get_by_name(self, name: str) -> OrgRole | None:
        stmt = select(OrgRoleORM).where(OrgRoleORM.name == name)
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._mapper.to_domain(orm) if orm else None

    async def get_system_roles(self) -> list[OrgRole]:
        stmt = select(OrgRoleORM).where(OrgRoleORM.is_system.is_(True))
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(o) for o in result.scalars().all()]

    async def get_by_org(self, org_id: Id) -> list[OrgRole]:
        uuid_val = self._mapper._map_uuid(org_id)
        stmt = select(OrgRoleORM).where(
            (OrgRoleORM.org_id == uuid_val) | (OrgRoleORM.is_system.is_(True))
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(o) for o in result.scalars().all()]

    async def get_by_org_and_name(self, org_id: Id, name: str) -> OrgRole | None:
        uuid_val = self._mapper._map_uuid(org_id)
        stmt = select(OrgRoleORM).where(
            OrgRoleORM.org_id == uuid_val,
            OrgRoleORM.name == name,
        )
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._mapper.to_domain(orm) if orm else None

    async def search(
        self,
        offset: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
    ) -> list[OrgRole]:
        stmt = select(OrgRoleORM)
        if filters:
            name = filters.get("name")
            if name:
                stmt = stmt.where(OrgRoleORM.name.ilike(f"%{name}%"))
            scope = filters.get("scope")
            if scope:
                stmt = stmt.where(OrgRoleORM.scope == scope)
            is_system = filters.get("is_system")
            if is_system is not None:
                stmt = stmt.where(OrgRoleORM.is_system.is_(is_system))
        stmt = stmt.offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(o) for o in result.scalars().all()]

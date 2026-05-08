from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.persistence.sqlalchemy_repository import SqlAlchemyRepository
from app.context.organization.domain.aggregates.organization import Organization
from app.context.organization.domain.repositories.organization_repository import OrganizationRepository
from app.context.organization.infrastructure.persistence.mappers.organization_mapper import OrganizationMapper
from app.context.organization.infrastructure.persistence.orm_models.organization_orm import (
    OrganizationORM,
    org_owners_table,
)


class SqlOrganizationRepository(SqlAlchemyRepository[Organization, OrganizationORM], OrganizationRepository):
    """SQLAlchemy-реализация OrganizationRepository."""

    def __init__(self, session: AsyncSession, mapper: OrganizationMapper) -> None:
        super().__init__(session=session, mapper=mapper, orm_model_class=OrganizationORM)

    # ------------------------------------------------------------------
    # Загрузка owner_ids из association table
    # ------------------------------------------------------------------

    async def _load_owner_ids(self, org_uuid) -> list[Id]:
        stmt = select(org_owners_table.c.user_id).where(
            org_owners_table.c.organization_id == org_uuid,
        )
        result = await self._session.execute(stmt)
        return [self._mapper._map_id(row[0]) for row in result.fetchall()]

    async def _enrich_with_owners(self, org: Organization, org_uuid) -> Organization:
        org.owner_ids = await self._load_owner_ids(org_uuid)
        return org

    # ------------------------------------------------------------------
    # Синхронизация owner_ids → association table
    # ------------------------------------------------------------------

    async def _sync_owners(self, org_uuid, owner_ids: list[Id]) -> None:
        await self._session.execute(
            org_owners_table.delete().where(org_owners_table.c.organization_id == org_uuid)
        )
        for owner_id in owner_ids:
            await self._session.execute(
                org_owners_table.insert().values(
                    organization_id=org_uuid,
                    user_id=self._mapper._map_uuid(owner_id),
                )
            )

    # ------------------------------------------------------------------
    # Override CRUD
    # ------------------------------------------------------------------

    async def get_by_id(self, id: Id) -> Organization | None:
        org = await super().get_by_id(id)
        if org is None:
            return None
        return await self._enrich_with_owners(org, self._mapper._map_uuid(id))

    async def add(self, aggregate: Organization) -> Organization:
        orm_model = self._mapper.to_orm(aggregate)
        self._session.add(orm_model)
        await self._session.flush()
        await self._sync_owners(orm_model.id, aggregate.owner_ids)
        await self._session.flush()
        return aggregate

    async def update(self, aggregate: Organization) -> Organization:
        result = await super().update(aggregate)
        uuid_val = self._mapper._map_uuid(aggregate.id)
        await self._sync_owners(uuid_val, aggregate.owner_ids)
        await self._session.flush()
        return result

    # ------------------------------------------------------------------
    # Специфичные методы доменного порта
    # ------------------------------------------------------------------

    async def get_by_owner(self, owner_id: Id) -> list[Organization]:
        uuid_val = self._mapper._map_uuid(owner_id)
        stmt = (
            select(OrganizationORM)
            .join(org_owners_table, OrganizationORM.id == org_owners_table.c.organization_id)
            .where(org_owners_table.c.user_id == uuid_val)
        )
        result = await self._session.execute(stmt)
        orgs = []
        for orm in result.scalars().all():
            org = self._mapper.to_domain(orm)
            org = await self._enrich_with_owners(org, orm.id)
            orgs.append(org)
        return orgs

    async def search(
        self,
        offset: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
    ) -> list[Organization]:
        stmt = select(OrganizationORM)
        if filters:
            name = filters.get("name")
            if name:
                safe = name.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
                stmt = stmt.where(OrganizationORM.name.ilike(f"%{safe}%", escape="\\"))
            status = filters.get("status")
            if status:
                stmt = stmt.where(OrganizationORM.status == status)
        stmt = stmt.offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        orgs = []
        for orm in result.scalars().all():
            org = self._mapper.to_domain(orm)
            org = await self._enrich_with_owners(org, orm.id)
            orgs.append(org)
        return orgs

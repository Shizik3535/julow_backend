from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.persistence.sqlalchemy_repository import SqlAlchemyRepository
from app.context.organization.domain.aggregates.department import Department
from app.context.organization.domain.repositories.department_repository import DepartmentRepository
from app.context.organization.infrastructure.persistence.mappers.department_mapper import DepartmentMapper
from app.context.organization.infrastructure.persistence.orm_models.department_orm import (
    DepartmentORM,
    department_members_table,
)


class SqlDepartmentRepository(SqlAlchemyRepository[Department, DepartmentORM], DepartmentRepository):
    """SQLAlchemy-реализация DepartmentRepository."""

    def __init__(self, session: AsyncSession, mapper: DepartmentMapper) -> None:
        super().__init__(session=session, mapper=mapper, orm_model_class=DepartmentORM)

    # ------------------------------------------------------------------
    # Загрузка / синхронизация member_ids
    # ------------------------------------------------------------------

    async def _load_member_ids(self, dept_uuid) -> list[Id]:
        stmt = select(department_members_table.c.user_id).where(
            department_members_table.c.department_id == dept_uuid,
        )
        result = await self._session.execute(stmt)
        return [self._mapper._map_id(row[0]) for row in result.fetchall()]

    async def _enrich_with_members(self, dept: Department, dept_uuid) -> Department:
        dept.member_ids = await self._load_member_ids(dept_uuid)
        return dept

    async def _sync_members(self, dept_uuid, member_ids: list[Id]) -> None:
        await self._session.execute(
            department_members_table.delete().where(
                department_members_table.c.department_id == dept_uuid
            )
        )
        for mid in member_ids:
            await self._session.execute(
                department_members_table.insert().values(
                    department_id=dept_uuid,
                    user_id=self._mapper._map_uuid(mid),
                )
            )

    # ------------------------------------------------------------------
    # Override CRUD
    # ------------------------------------------------------------------

    async def get_by_id(self, id: Id) -> Department | None:
        dept = await super().get_by_id(id)
        if dept is None:
            return None
        return await self._enrich_with_members(dept, self._mapper._map_uuid(id))

    async def add(self, aggregate: Department) -> Department:
        orm_model = self._mapper.to_orm(aggregate)
        self._session.add(orm_model)
        await self._session.flush()
        await self._sync_members(orm_model.id, aggregate.member_ids)
        await self._session.flush()
        return aggregate

    async def update(self, aggregate: Department) -> Department:
        result = await super().update(aggregate)
        uuid_val = self._mapper._map_uuid(aggregate.id)
        await self._sync_members(uuid_val, aggregate.member_ids)
        await self._session.flush()
        return result

    # ------------------------------------------------------------------
    # Специфичные методы
    # ------------------------------------------------------------------

    async def get_by_org_id(self, org_id: Id) -> list[Department]:
        uuid_val = self._mapper._map_uuid(org_id)
        stmt = select(DepartmentORM).where(DepartmentORM.org_id == uuid_val)
        result = await self._session.execute(stmt)
        depts = []
        for orm in result.scalars().all():
            dept = self._mapper.to_domain(orm)
            dept = await self._enrich_with_members(dept, orm.id)
            depts.append(dept)
        return depts

    async def get_by_parent(self, parent_id: Id) -> list[Department]:
        uuid_val = self._mapper._map_uuid(parent_id)
        stmt = select(DepartmentORM).where(DepartmentORM.parent_id == uuid_val)
        result = await self._session.execute(stmt)
        depts = []
        for orm in result.scalars().all():
            dept = self._mapper.to_domain(orm)
            dept = await self._enrich_with_members(dept, orm.id)
            depts.append(dept)
        return depts

    async def get_by_member(self, user_id: Id) -> list[Department]:
        uuid_val = self._mapper._map_uuid(user_id)
        stmt = (
            select(DepartmentORM)
            .join(department_members_table, DepartmentORM.id == department_members_table.c.department_id)
            .where(department_members_table.c.user_id == uuid_val)
        )
        result = await self._session.execute(stmt)
        depts = []
        for orm in result.scalars().all():
            dept = self._mapper.to_domain(orm)
            dept = await self._enrich_with_members(dept, orm.id)
            depts.append(dept)
        return depts

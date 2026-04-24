from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.domain.exceptions.entity_not_found_exception import EntityNotFoundException
from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.persistence.sqlalchemy_repository import SqlAlchemyRepository
from app.context.organization.domain.aggregates.org_membership import OrgMembership
from app.context.organization.domain.entities.org_member import OrgMember
from app.context.organization.domain.repositories.org_membership_repository import OrgMembershipRepository
from app.context.organization.infrastructure.persistence.mappers.org_membership_mapper import OrgMembershipMapper
from app.context.organization.infrastructure.persistence.orm_models.org_membership_orm import (
    OrgMemberORM,
    OrgMembershipORM,
)


class SqlOrgMembershipRepository(SqlAlchemyRepository[OrgMembership, OrgMembershipORM], OrgMembershipRepository):
    """SQLAlchemy-реализация OrgMembershipRepository."""

    def __init__(self, session: AsyncSession, mapper: OrgMembershipMapper) -> None:
        super().__init__(session=session, mapper=mapper, orm_model_class=OrgMembershipORM)

    # ------------------------------------------------------------------
    # Специфичные методы
    # ------------------------------------------------------------------

    async def get_by_org_id(self, org_id: Id) -> OrgMembership | None:
        uuid_val = self._mapper._map_uuid(org_id)
        stmt = select(OrgMembershipORM).where(OrgMembershipORM.org_id == uuid_val)
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._mapper.to_domain(orm) if orm else None

    async def get_member_by_org_and_user(self, org_id: Id, user_id: Id) -> OrgMember | None:
        org_uuid = self._mapper._map_uuid(org_id)
        user_uuid = self._mapper._map_uuid(user_id)
        stmt = (
            select(OrgMemberORM)
            .join(OrgMembershipORM, OrgMemberORM.membership_id == OrgMembershipORM.id)
            .where(OrgMembershipORM.org_id == org_uuid, OrgMemberORM.user_id == user_uuid)
        )
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        if orm is None:
            return None
        return self._mapper._member_to_domain(orm)

    async def get_members_by_org(self, org_id: Id) -> list[OrgMember]:
        org_uuid = self._mapper._map_uuid(org_id)
        stmt = (
            select(OrgMemberORM)
            .join(OrgMembershipORM, OrgMemberORM.membership_id == OrgMembershipORM.id)
            .where(OrgMembershipORM.org_id == org_uuid)
        )
        result = await self._session.execute(stmt)
        return [self._mapper._member_to_domain(orm) for orm in result.scalars().all()]

    # ------------------------------------------------------------------
    # Override update для синхронизации дочерних OrgMember
    # ------------------------------------------------------------------

    async def update(self, aggregate: OrgMembership) -> OrgMembership:
        uuid_val = self._mapper._map_uuid(aggregate.id)
        stmt = select(OrgMembershipORM).where(OrgMembershipORM.id == uuid_val)
        result = await self._session.execute(stmt)
        orm_model = result.scalar_one_or_none()
        if orm_model is None:
            raise EntityNotFoundException(entity_type="OrgMembership", id=aggregate.id)

        # Обновить скалярные поля
        orm_model.org_id = self._mapper._map_uuid(aggregate.org_id)
        orm_model.updated_at = aggregate.updated_at

        # Синхронизация дочерних: delete old + insert new
        await self._session.execute(
            OrgMemberORM.__table__.delete().where(OrgMemberORM.membership_id == uuid_val)
        )
        updated_orm = self._mapper.to_orm(aggregate)
        for member_orm in updated_orm.members:
            member_orm.membership_id = uuid_val
            self._session.add(member_orm)

        await self._session.flush()
        return aggregate

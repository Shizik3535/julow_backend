from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.persistence.sqlalchemy_repository import SqlAlchemyRepository
from app.context.organization.domain.aggregates.invitation import Invitation
from app.context.organization.domain.repositories.invitation_repository import InvitationRepository
from app.context.organization.infrastructure.persistence.mappers.invitation_mapper import InvitationMapper
from app.context.organization.infrastructure.persistence.orm_models.invitation_orm import InvitationORM


class SqlInvitationRepository(SqlAlchemyRepository[Invitation, InvitationORM], InvitationRepository):
    """SQLAlchemy-реализация InvitationRepository."""

    def __init__(self, session: AsyncSession, mapper: InvitationMapper) -> None:
        super().__init__(session=session, mapper=mapper, orm_model_class=InvitationORM)

    async def get_by_org_id(self, org_id: Id) -> list[Invitation]:
        uuid_val = self._mapper._map_uuid(org_id)
        stmt = select(InvitationORM).where(InvitationORM.org_id == uuid_val)
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(o) for o in result.scalars().all()]

    async def get_by_token(self, token_value: str) -> Invitation | None:
        stmt = select(InvitationORM).where(InvitationORM.link_value == token_value)
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._mapper.to_domain(orm) if orm else None

    async def get_pending_by_org(self, org_id: Id) -> list[Invitation]:
        uuid_val = self._mapper._map_uuid(org_id)
        stmt = select(InvitationORM).where(
            InvitationORM.org_id == uuid_val,
            InvitationORM.status == "pending",
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(o) for o in result.scalars().all()]

from __future__ import annotations

from typing import Any

from sqlalchemy import func, or_, select
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

    async def search_by_user(
        self,
        email: str,
        user_id: Id | None = None,
        offset: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
    ) -> tuple[list[Invitation], int]:
        conditions = []
        # PENDING приглашения по email
        conditions.append(
            (InvitationORM.email == email) & (InvitationORM.status == "pending")
        )
        # Принятые/отклонённые по user_id
        if user_id is not None:
            uuid_val = self._mapper._map_uuid(user_id)
            conditions.append(InvitationORM.user_id == uuid_val)

        base_cond = or_(*conditions)

        # Дополнительные фильтры
        stmt = select(InvitationORM).where(base_cond)
        count_stmt = select(func.count()).select_from(InvitationORM).where(base_cond)

        if filters:
            if "status" in filters:
                stmt = stmt.where(InvitationORM.status == filters["status"])
                count_stmt = count_stmt.where(InvitationORM.status == filters["status"])
            if "org_id" in filters:
                org_uuid = self._mapper._map_uuid(Id.from_string(filters["org_id"]))
                stmt = stmt.where(InvitationORM.org_id == org_uuid)
                count_stmt = count_stmt.where(InvitationORM.org_id == org_uuid)
            if "search_text" in filters:
                pattern = f"%{filters['search_text']}%"
                stmt = stmt.where(InvitationORM.email.ilike(pattern))
                count_stmt = count_stmt.where(InvitationORM.email.ilike(pattern))

        # Count
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar_one()

        # Data
        stmt = stmt.offset(offset).limit(limit).order_by(InvitationORM.invited_at.desc())
        result = await self._session.execute(stmt)
        orm_models = result.scalars().all()
        aggregates = [self._mapper.to_domain(o) for o in orm_models]

        return aggregates, total

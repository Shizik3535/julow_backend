from __future__ import annotations

from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.persistence.sqlalchemy_repository import SqlAlchemyRepository
from app.context.project.domain.aggregates.project_invitation import ProjectInvitation
from app.context.project.domain.repositories.project_invitation_repository import (
    ProjectInvitationRepository,
)
from app.context.project.infrastructure.persistence.mappers.project_invitation_mapper import (
    ProjectInvitationMapper,
)
from app.context.project.infrastructure.persistence.orm_models.project_invitation_orm import (
    ProjectInvitationORM,
)


class SqlProjectInvitationRepository(
    SqlAlchemyRepository[ProjectInvitation, ProjectInvitationORM],
    ProjectInvitationRepository,
):
    """SQLAlchemy-реализация ProjectInvitationRepository."""

    def __init__(self, session: AsyncSession, mapper: ProjectInvitationMapper) -> None:
        super().__init__(session=session, mapper=mapper, orm_model_class=ProjectInvitationORM)

    # ------------------------------------------------------------------
    # Специфичные методы
    # ------------------------------------------------------------------

    async def get_by_project_id(self, project_id: Id) -> list[ProjectInvitation]:
        uuid_val = self._mapper._map_uuid(project_id)
        stmt = select(ProjectInvitationORM).where(ProjectInvitationORM.project_id == uuid_val)
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(orm) for orm in result.scalars().all()]

    async def get_by_token(self, token_value: str) -> ProjectInvitation | None:
        stmt = select(ProjectInvitationORM).where(ProjectInvitationORM.token_value == token_value)
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._mapper.to_domain(orm) if orm else None

    async def get_pending_by_project(self, project_id: Id) -> list[ProjectInvitation]:
        uuid_val = self._mapper._map_uuid(project_id)
        stmt = select(ProjectInvitationORM).where(
            ProjectInvitationORM.project_id == uuid_val,
            ProjectInvitationORM.status == "pending",
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(orm) for orm in result.scalars().all()]

    async def search_by_user(
        self,
        email: str,
        user_id: Id | None = None,
        offset: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
    ) -> tuple[list[ProjectInvitation], int]:
        conditions = []
        # PENDING приглашения по email
        conditions.append(
            (ProjectInvitationORM.email == email) & (ProjectInvitationORM.status == "pending")
        )
        # Принятые/отклонённые по user_id
        if user_id is not None:
            uuid_val = self._mapper._map_uuid(user_id)
            conditions.append(ProjectInvitationORM.user_id == uuid_val)

        base_cond = or_(*conditions)

        stmt = select(ProjectInvitationORM).where(base_cond)
        count_stmt = select(func.count()).select_from(ProjectInvitationORM).where(base_cond)

        if filters:
            if "status" in filters:
                stmt = stmt.where(ProjectInvitationORM.status == filters["status"])
                count_stmt = count_stmt.where(ProjectInvitationORM.status == filters["status"])
            if "project_id" in filters:
                proj_uuid = self._mapper._map_uuid(Id.from_string(filters["project_id"]))
                stmt = stmt.where(ProjectInvitationORM.project_id == proj_uuid)
                count_stmt = count_stmt.where(ProjectInvitationORM.project_id == proj_uuid)
            if "search_text" in filters:
                pattern = f"%{filters['search_text']}%"
                stmt = stmt.where(ProjectInvitationORM.email.ilike(pattern))
                count_stmt = count_stmt.where(ProjectInvitationORM.email.ilike(pattern))

        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar_one()

        stmt = stmt.offset(offset).limit(limit).order_by(ProjectInvitationORM.invited_at.desc())
        result = await self._session.execute(stmt)
        orm_models = result.scalars().all()
        aggregates = [self._mapper.to_domain(orm) for orm in orm_models]

        return aggregates, total

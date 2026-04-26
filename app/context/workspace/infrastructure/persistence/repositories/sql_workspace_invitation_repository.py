from __future__ import annotations

from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.persistence.sqlalchemy_repository import SqlAlchemyRepository
from app.context.workspace.domain.aggregates.workspace_invitation import WorkspaceInvitation
from app.context.workspace.domain.repositories.workspace_invitation_repository import WorkspaceInvitationRepository
from app.context.workspace.infrastructure.persistence.mappers.workspace_invitation_mapper import WorkspaceInvitationMapper
from app.context.workspace.infrastructure.persistence.orm_models.workspace_invitation_orm import WorkspaceInvitationORM


class SqlWorkspaceInvitationRepository(
    SqlAlchemyRepository[WorkspaceInvitation, WorkspaceInvitationORM],
    WorkspaceInvitationRepository,
):
    """SQLAlchemy-реализация WorkspaceInvitationRepository."""

    def __init__(self, session: AsyncSession, mapper: WorkspaceInvitationMapper) -> None:
        super().__init__(session=session, mapper=mapper, orm_model_class=WorkspaceInvitationORM)

    # ------------------------------------------------------------------
    # Специфичные методы
    # ------------------------------------------------------------------

    async def get_by_workspace_id(self, workspace_id: Id) -> list[WorkspaceInvitation]:
        uuid_val = self._mapper._map_uuid(workspace_id)
        stmt = select(WorkspaceInvitationORM).where(WorkspaceInvitationORM.workspace_id == uuid_val)
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(orm) for orm in result.scalars().all()]

    async def get_by_token(self, token_value: str) -> WorkspaceInvitation | None:
        stmt = select(WorkspaceInvitationORM).where(WorkspaceInvitationORM.token_value == token_value)
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._mapper.to_domain(orm) if orm else None

    async def get_pending_by_workspace(self, workspace_id: Id) -> list[WorkspaceInvitation]:
        uuid_val = self._mapper._map_uuid(workspace_id)
        stmt = select(WorkspaceInvitationORM).where(
            WorkspaceInvitationORM.workspace_id == uuid_val,
            WorkspaceInvitationORM.status == "pending",
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
    ) -> tuple[list[WorkspaceInvitation], int]:
        conditions = []
        # PENDING приглашения по email
        conditions.append(
            (WorkspaceInvitationORM.email == email) & (WorkspaceInvitationORM.status == "pending")
        )
        # Принятые/отклонённые по user_id
        if user_id is not None:
            uuid_val = self._mapper._map_uuid(user_id)
            conditions.append(WorkspaceInvitationORM.user_id == uuid_val)

        base_cond = or_(*conditions)

        # Дополнительные фильтры
        stmt = select(WorkspaceInvitationORM).where(base_cond)
        count_stmt = select(func.count()).select_from(WorkspaceInvitationORM).where(base_cond)

        if filters:
            if "status" in filters:
                stmt = stmt.where(WorkspaceInvitationORM.status == filters["status"])
                count_stmt = count_stmt.where(WorkspaceInvitationORM.status == filters["status"])
            if "workspace_id" in filters:
                ws_uuid = self._mapper._map_uuid(Id.from_string(filters["workspace_id"]))
                stmt = stmt.where(WorkspaceInvitationORM.workspace_id == ws_uuid)
                count_stmt = count_stmt.where(WorkspaceInvitationORM.workspace_id == ws_uuid)
            if "search_text" in filters:
                pattern = f"%{filters['search_text']}%"
                stmt = stmt.where(WorkspaceInvitationORM.email.ilike(pattern))
                count_stmt = count_stmt.where(WorkspaceInvitationORM.email.ilike(pattern))

        # Count
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar_one()

        # Data
        stmt = stmt.offset(offset).limit(limit).order_by(WorkspaceInvitationORM.invited_at.desc())
        result = await self._session.execute(stmt)
        orm_models = result.scalars().all()
        aggregates = [self._mapper.to_domain(orm) for orm in orm_models]

        return aggregates, total

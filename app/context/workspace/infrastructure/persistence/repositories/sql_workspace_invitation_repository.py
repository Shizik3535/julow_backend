from __future__ import annotations

from sqlalchemy import select
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

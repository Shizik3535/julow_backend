from __future__ import annotations

from sqlalchemy import select, type_coerce
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.persistence.sqlalchemy_repository import SqlAlchemyRepository
from app.context.workspace.domain.aggregates.workspace_team import WorkspaceTeam
from app.context.workspace.domain.repositories.workspace_team_repository import WorkspaceTeamRepository
from app.context.workspace.infrastructure.persistence.mappers.workspace_team_mapper import WorkspaceTeamMapper
from app.context.workspace.infrastructure.persistence.orm_models.workspace_team_orm import WorkspaceTeamORM


class SqlWorkspaceTeamRepository(SqlAlchemyRepository[WorkspaceTeam, WorkspaceTeamORM], WorkspaceTeamRepository):
    """SQLAlchemy-реализация WorkspaceTeamRepository."""

    def __init__(self, session: AsyncSession, mapper: WorkspaceTeamMapper) -> None:
        super().__init__(session=session, mapper=mapper, orm_model_class=WorkspaceTeamORM)

    # ------------------------------------------------------------------
    # Специфичные методы
    # ------------------------------------------------------------------

    async def get_by_workspace(self, workspace_id: Id) -> list[WorkspaceTeam]:
        uuid_val = self._mapper._map_uuid(workspace_id)
        stmt = select(WorkspaceTeamORM).where(WorkspaceTeamORM.workspace_id == uuid_val)
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(orm) for orm in result.scalars().all()]

    async def get_by_member(self, user_id: Id) -> list[WorkspaceTeam]:
        uuid_val = self._mapper._map_uuid(user_id)
        # member_ids хранится как JSONB-массив строк UUID
        stmt = select(WorkspaceTeamORM).where(
            WorkspaceTeamORM.member_ids.bool_op("@>")(type_coerce(str(uuid_val), JSONB))
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(orm) for orm in result.scalars().all()]

    async def get_by_lead(self, user_id: Id) -> list[WorkspaceTeam]:
        uuid_val = self._mapper._map_uuid(user_id)
        stmt = select(WorkspaceTeamORM).where(WorkspaceTeamORM.lead_id == uuid_val)
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(orm) for orm in result.scalars().all()]

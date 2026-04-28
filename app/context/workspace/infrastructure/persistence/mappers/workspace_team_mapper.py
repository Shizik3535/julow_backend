from __future__ import annotations

from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.persistence.sqlalchemy_base_mapper import BaseMapper

from app.context.workspace.domain.aggregates.workspace_team import WorkspaceTeam
from app.context.workspace.infrastructure.persistence.orm_models.workspace_team_orm import WorkspaceTeamORM


class WorkspaceTeamMapper(BaseMapper[WorkspaceTeam, WorkspaceTeamORM]):
    """Data Mapper: WorkspaceTeam ↔ WorkspaceTeamORM."""

    # ------------------------------------------------------------------
    # ORM → Domain
    # ------------------------------------------------------------------

    def to_domain(self, orm_model: WorkspaceTeamORM) -> WorkspaceTeam:
        return WorkspaceTeam(
            id=self._map_id(orm_model.id),
            workspace_id=self._map_id(orm_model.workspace_id),
            name=orm_model.name,
            description=orm_model.description,
            lead_id=self._map_id(orm_model.lead_id) if orm_model.lead_id else None,
            member_ids=[self._map_id(uid) for uid in (orm_model.member_ids or [])],
            icon=orm_model.icon if orm_model.icon else None,
            is_active=orm_model.is_active,
            created_at=orm_model.created_at,
            updated_at=orm_model.updated_at,
        )

    # ------------------------------------------------------------------
    # Domain → ORM
    # ------------------------------------------------------------------

    def to_orm(self, aggregate: WorkspaceTeam) -> WorkspaceTeamORM:
        return WorkspaceTeamORM(
            id=self._map_uuid(aggregate.id),
            workspace_id=self._map_uuid(aggregate.workspace_id),
            name=aggregate.name,
            description=aggregate.description,
            lead_id=self._map_uuid(aggregate.lead_id) if aggregate.lead_id else None,
            member_ids=[str(self._map_uuid(mid)) for mid in aggregate.member_ids],
            icon=aggregate.icon if aggregate.icon else None,
            is_active=aggregate.is_active,
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,
        )

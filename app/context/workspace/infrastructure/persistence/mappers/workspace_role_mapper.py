from __future__ import annotations

from app.shared.infrastructure.persistence.sqlalchemy_base_mapper import BaseMapper

from app.context.workspace.domain.aggregates.workspace_role import WorkspaceRole
from app.context.workspace.infrastructure.persistence.orm_models.workspace_role_orm import WorkspaceRoleORM


class WorkspaceRoleMapper(BaseMapper[WorkspaceRole, WorkspaceRoleORM]):
    """Data Mapper: WorkspaceRole ↔ WorkspaceRoleORM."""

    # ------------------------------------------------------------------
    # ORM → Domain
    # ------------------------------------------------------------------

    def to_domain(self, orm_model: WorkspaceRoleORM) -> WorkspaceRole:
        return WorkspaceRole(
            id=self._map_id(orm_model.id),
            workspace_id=self._map_id(orm_model.workspace_id) if orm_model.workspace_id else None,
            name=orm_model.name,
            permissions=orm_model.permissions or [],
            is_system=orm_model.is_system,
            description=orm_model.description,
            created_at=orm_model.created_at,
            updated_at=orm_model.updated_at,
        )

    # ------------------------------------------------------------------
    # Domain → ORM
    # ------------------------------------------------------------------

    def to_orm(self, aggregate: WorkspaceRole) -> WorkspaceRoleORM:
        return WorkspaceRoleORM(
            id=self._map_uuid(aggregate.id),
            workspace_id=self._map_uuid(aggregate.workspace_id) if aggregate.workspace_id else None,
            name=aggregate.name,
            permissions=aggregate.permissions,
            is_system=aggregate.is_system,
            description=aggregate.description,
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,
        )

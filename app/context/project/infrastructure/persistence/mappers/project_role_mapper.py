from __future__ import annotations

from app.shared.infrastructure.persistence.sqlalchemy_base_mapper import BaseMapper
from app.context.project.domain.aggregates.project_role import ProjectRole
from app.context.project.infrastructure.persistence.orm_models.project_role_orm import ProjectRoleORM


class ProjectRoleMapper(BaseMapper[ProjectRole, ProjectRoleORM]):
    """Data Mapper: ProjectRole ↔ ProjectRoleORM."""

    def to_domain(self, orm_model: ProjectRoleORM) -> ProjectRole:
        return ProjectRole(
            id=self._map_id(orm_model.id),
            project_id=self._map_id(orm_model.project_id) if orm_model.project_id else None,
            name=orm_model.name,
            permissions=list(orm_model.permissions) if orm_model.permissions else [],
            is_system=orm_model.is_system,
            description=orm_model.description,
            created_at=orm_model.created_at,
            updated_at=orm_model.updated_at,
        )

    def to_orm(self, aggregate: ProjectRole) -> ProjectRoleORM:
        return ProjectRoleORM(
            id=self._map_uuid(aggregate.id),
            project_id=self._map_uuid(aggregate.project_id) if aggregate.project_id else None,
            name=aggregate.name,
            permissions=aggregate.permissions,
            is_system=aggregate.is_system,
            description=aggregate.description,
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,
        )

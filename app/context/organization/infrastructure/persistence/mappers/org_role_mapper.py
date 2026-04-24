from __future__ import annotations

from app.shared.infrastructure.persistence.sqlalchemy_base_mapper import BaseMapper

from app.context.organization.domain.aggregates.org_role import OrgRole
from app.context.organization.domain.value_objects.org_role_scope import OrgRoleScope
from app.context.organization.infrastructure.persistence.orm_models.org_role_orm import OrgRoleORM


class OrgRoleMapper(BaseMapper[OrgRole, OrgRoleORM]):
    """Data Mapper: OrgRole ↔ OrgRoleORM."""

    def to_domain(self, orm_model: OrgRoleORM) -> OrgRole:
        return OrgRole(
            id=self._map_id(orm_model.id),
            org_id=self._map_id(orm_model.org_id) if orm_model.org_id else None,
            name=orm_model.name,
            permissions=orm_model.permissions or [],
            is_system=orm_model.is_system,
            description=orm_model.description,
            scope=OrgRoleScope(orm_model.scope),
            created_at=orm_model.created_at,
            updated_at=orm_model.updated_at,
        )

    def to_orm(self, aggregate: OrgRole) -> OrgRoleORM:
        return OrgRoleORM(
            id=self._map_uuid(aggregate.id),
            org_id=self._map_uuid(aggregate.org_id) if aggregate.org_id else None,
            name=aggregate.name,
            permissions=aggregate.permissions,
            is_system=aggregate.is_system,
            description=aggregate.description,
            scope=aggregate.scope.value,
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,
        )

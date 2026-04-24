from __future__ import annotations

from app.context.identity.domain.aggregates.role import Role
from app.context.identity.infrastructure.persistence.orm_models.role_orm import RoleORM
from app.shared.infrastructure.persistence.sqlalchemy_base_mapper import BaseMapper


class RoleMapper(BaseMapper[Role, RoleORM]):
    """Data Mapper: Role ↔ RoleORM."""

    def to_domain(self, orm_model: RoleORM) -> Role:
        return Role(
            id=self._map_id(orm_model.id),
            name=orm_model.name,
            permissions=list(orm_model.permissions) if orm_model.permissions else [],
            is_system=orm_model.is_system,
            description=orm_model.description,
        )

    def to_orm(self, aggregate: Role) -> RoleORM:
        return RoleORM(
            id=self._map_uuid(aggregate.id),
            name=aggregate.name,
            permissions=aggregate.permissions,
            is_system=aggregate.is_system,
            description=aggregate.description,
        )

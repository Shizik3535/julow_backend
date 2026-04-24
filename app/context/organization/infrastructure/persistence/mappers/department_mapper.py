from __future__ import annotations

from app.shared.infrastructure.persistence.sqlalchemy_base_mapper import BaseMapper

from app.context.organization.domain.aggregates.department import Department
from app.context.organization.infrastructure.persistence.orm_models.department_orm import DepartmentORM


class DepartmentMapper(BaseMapper[Department, DepartmentORM]):
    """Data Mapper: Department ↔ DepartmentORM.

    member_ids маппятся отдельно в репозитории через association table.
    """

    def to_domain(self, orm_model: DepartmentORM) -> Department:
        return Department(
            id=self._map_id(orm_model.id),
            org_id=self._map_id(orm_model.org_id),
            name=orm_model.name,
            parent_id=self._map_id(orm_model.parent_id) if orm_model.parent_id else None,
            lead_id=self._map_id(orm_model.lead_id) if orm_model.lead_id else None,
            member_ids=[],  # заполняется в repo через association table
            is_active=orm_model.is_active,
            created_at=orm_model.created_at,
            updated_at=orm_model.updated_at,
        )

    def to_orm(self, aggregate: Department) -> DepartmentORM:
        return DepartmentORM(
            id=self._map_uuid(aggregate.id),
            org_id=self._map_uuid(aggregate.org_id),
            name=aggregate.name,
            parent_id=self._map_uuid(aggregate.parent_id) if aggregate.parent_id else None,
            lead_id=self._map_uuid(aggregate.lead_id) if aggregate.lead_id else None,
            is_active=aggregate.is_active,
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,
        )

from __future__ import annotations

from app.shared.domain.value_objects.color_vo import Color
from app.shared.infrastructure.persistence.sqlalchemy_base_mapper import BaseMapper

from app.context.timetracking.domain.aggregates.activity_category import ActivityCategory
from app.context.timetracking.infrastructure.persistence.orm_models.activity_category_orm import (
    ActivityCategoryORM,
)


class ActivityCategoryMapper(BaseMapper[ActivityCategory, ActivityCategoryORM]):
    """Data Mapper: ActivityCategory ↔ ActivityCategoryORM."""

    def to_domain(self, orm_model: ActivityCategoryORM) -> ActivityCategory:
        return ActivityCategory(
            id=self._map_id(orm_model.id),
            workspace_id=self._map_id(orm_model.workspace_id) if orm_model.workspace_id else None,
            name=orm_model.name,
            color=Color(value=orm_model.color) if orm_model.color else None,
            is_system=orm_model.is_system,
            description=orm_model.description,
            is_deleted=orm_model.is_deleted,
            created_at=orm_model.created_at,
            updated_at=orm_model.updated_at,
        )

    def to_orm(self, aggregate: ActivityCategory) -> ActivityCategoryORM:
        return ActivityCategoryORM(
            id=self._map_uuid(aggregate.id),
            workspace_id=self._map_uuid(aggregate.workspace_id) if aggregate.workspace_id else None,
            name=aggregate.name,
            color=aggregate.color.value if aggregate.color else None,
            is_system=aggregate.is_system,
            description=aggregate.description,
            is_deleted=aggregate.is_deleted,
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,
        )

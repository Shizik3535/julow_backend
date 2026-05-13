from __future__ import annotations

from app.shared.domain.value_objects.color_vo import Color
from app.shared.infrastructure.persistence.sqlalchemy_base_mapper import BaseMapper

from app.context.timetracking.domain.aggregates.time_entry_tag import TimeEntryTag
from app.context.timetracking.infrastructure.persistence.orm_models.time_entry_tag_orm import (
    TimeEntryTagORM,
)


class TimeEntryTagMapper(BaseMapper[TimeEntryTag, TimeEntryTagORM]):
    """Data Mapper: TimeEntryTag ↔ TimeEntryTagORM."""

    def to_domain(self, orm_model: TimeEntryTagORM) -> TimeEntryTag:
        return TimeEntryTag(
            id=self._map_id(orm_model.id),
            workspace_id=self._map_id(orm_model.workspace_id),
            name=orm_model.name,
            color=Color(value=orm_model.color) if orm_model.color else None,
            is_deleted=orm_model.is_deleted,
            created_at=orm_model.created_at,
            updated_at=orm_model.updated_at,
        )

    def to_orm(self, aggregate: TimeEntryTag) -> TimeEntryTagORM:
        return TimeEntryTagORM(
            id=self._map_uuid(aggregate.id),
            workspace_id=self._map_uuid(aggregate.workspace_id),
            name=aggregate.name,
            color=aggregate.color.value if aggregate.color else None,
            is_deleted=aggregate.is_deleted,
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,
        )

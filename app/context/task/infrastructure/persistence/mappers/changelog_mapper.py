from __future__ import annotations

from app.shared.infrastructure.persistence.sqlalchemy_base_mapper import BaseMapper

from app.context.task.domain.aggregates.changelog import ChangelogEntry
from app.context.task.infrastructure.persistence.orm_models.changelog_orm import ChangelogEntryORM


class ChangelogMapper(BaseMapper[ChangelogEntry, ChangelogEntryORM]):
    """Data Mapper: ChangelogEntry ↔ ChangelogEntryORM."""

    def to_domain(self, orm_model: ChangelogEntryORM) -> ChangelogEntry:
        return ChangelogEntry(
            id=self._map_id(orm_model.id),
            task_id=self._map_id(orm_model.task_id),
            field_name=orm_model.field_name,
            old_value=orm_model.old_value,
            new_value=orm_model.new_value,
            changed_by=self._map_id(orm_model.changed_by),
            changed_at=orm_model.changed_at,
            created_at=orm_model.created_at,
            updated_at=orm_model.updated_at,
        )

    def to_orm(self, aggregate: ChangelogEntry) -> ChangelogEntryORM:
        return ChangelogEntryORM(
            id=self._map_uuid(aggregate.id),
            task_id=self._map_uuid(aggregate.task_id),
            field_name=aggregate.field_name,
            old_value=aggregate.old_value,
            new_value=aggregate.new_value,
            changed_by=self._map_uuid(aggregate.changed_by),
            changed_at=aggregate.changed_at,
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,
        )

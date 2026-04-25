from __future__ import annotations

from app.shared.infrastructure.persistence.sqlalchemy_base_mapper import BaseMapper
from app.shared.domain.value_objects.color_vo import Color
from app.shared.domain.value_objects.rich_text_vo import RichText
from app.shared.domain.value_objects.rich_text_format import RichTextFormat
from app.context.project.domain.aggregates.epic import Epic
from app.context.project.domain.value_objects.epic_status import EpicStatus
from app.context.project.infrastructure.persistence.orm_models.epic_orm import EpicORM


class EpicMapper(BaseMapper[Epic, EpicORM]):
    """Data Mapper: Epic ↔ EpicORM."""

    def to_domain(self, orm_model: EpicORM) -> Epic:
        description = None
        if orm_model.description_raw is not None:
            fmt = RichTextFormat(orm_model.description_format) if orm_model.description_format else RichTextFormat.MARKDOWN
            description = RichText(content=orm_model.description_raw, format=fmt)

        color = Color(orm_model.color) if orm_model.color else None

        return Epic(
            id=self._map_id(orm_model.id),
            project_id=self._map_id(orm_model.project_id),
            name=orm_model.name,
            description=description,
            status=EpicStatus(orm_model.status),
            start_date=orm_model.start_date,
            due_date=orm_model.due_date,
            owner_id=self._map_id(orm_model.owner_id) if orm_model.owner_id else None,
            color=color,
            created_at=orm_model.created_at,
            updated_at=orm_model.updated_at,
        )

    def to_orm(self, aggregate: Epic) -> EpicORM:
        description_format = None
        description_raw = None
        if aggregate.description is not None:
            description_format = aggregate.description.format.value
            description_raw = aggregate.description.content

        color = str(aggregate.color) if aggregate.color else None

        return EpicORM(
            id=self._map_uuid(aggregate.id),
            project_id=self._map_uuid(aggregate.project_id),
            name=aggregate.name,
            description_format=description_format,
            description_raw=description_raw,
            status=aggregate.status.value,
            start_date=aggregate.start_date,
            due_date=aggregate.due_date,
            owner_id=self._map_uuid(aggregate.owner_id) if aggregate.owner_id else None,
            color=color,
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,
        )

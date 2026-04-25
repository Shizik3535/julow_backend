from __future__ import annotations

from app.shared.infrastructure.persistence.sqlalchemy_base_mapper import BaseMapper
from app.context.project.domain.aggregates.retro_template import RetroTemplate
from app.context.project.domain.value_objects.retro_section import RetroSection
from app.context.project.domain.value_objects.retro_item_type import RetroItemType
from app.context.project.infrastructure.persistence.orm_models.retro_template_orm import RetroTemplateORM


class RetroTemplateMapper(BaseMapper[RetroTemplate, RetroTemplateORM]):
    """Data Mapper: RetroTemplate ↔ RetroTemplateORM."""

    def to_domain(self, orm_model: RetroTemplateORM) -> RetroTemplate:
        sections = [
            RetroSection(
                title=s["title"],
                prompt=s.get("prompt"),
                item_type=RetroItemType(s.get("item_type", "neutral")),
            )
            for s in orm_model.sections
        ]

        return RetroTemplate(
            id=self._map_id(orm_model.id),
            name=orm_model.name,
            sections=sections,
            is_system=orm_model.is_system,
            created_at=orm_model.created_at,
            updated_at=orm_model.updated_at,
        )

    def to_orm(self, aggregate: RetroTemplate) -> RetroTemplateORM:
        sections = [
            {
                "title": s.title,
                "prompt": s.prompt,
                "item_type": s.item_type.value,
            }
            for s in aggregate.sections
        ]

        return RetroTemplateORM(
            id=self._map_uuid(aggregate.id),
            name=aggregate.name,
            sections=sections,
            is_system=aggregate.is_system,
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,
        )

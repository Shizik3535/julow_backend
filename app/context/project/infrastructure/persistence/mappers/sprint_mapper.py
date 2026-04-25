from __future__ import annotations

from app.shared.infrastructure.persistence.sqlalchemy_base_mapper import BaseMapper
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.date_range_vo import DateRange
from app.context.project.domain.aggregates.sprint import Sprint
from app.context.project.domain.value_objects.sprint_status import SprintStatus
from app.context.project.domain.value_objects.sprint_goal import SprintGoal
from app.context.project.domain.value_objects.retro_section import RetroSection
from app.context.project.domain.value_objects.retro_item_type import RetroItemType
from app.context.project.domain.entities.sprint_retro import SprintRetro
from app.context.project.domain.entities.retro_item import RetroItem
from app.context.project.infrastructure.persistence.orm_models.sprint_orm import (
    SprintORM,
    SprintRetroORM,
    RetroItemORM,
)


class SprintMapper(BaseMapper[Sprint, SprintORM]):
    """Data Mapper: Sprint ↔ SprintORM."""

    def to_domain(self, orm_model: SprintORM) -> Sprint:
        # DateRange
        date_range = None
        if orm_model.sprint_start is not None and orm_model.sprint_end is not None:
            date_range = DateRange(start=orm_model.sprint_start, end=orm_model.sprint_end)

        # SprintGoal
        goal = SprintGoal(value=orm_model.goal) if orm_model.goal else None

        # SprintRetro
        retro = None
        if orm_model.retro is not None:
            retro = self._retro_orm_to_domain(orm_model.retro)

        return Sprint(
            id=self._map_id(orm_model.id),
            project_id=self._map_id(orm_model.project_id),
            name=orm_model.name,
            goal=goal,
            status=SprintStatus(orm_model.status),
            date_range=date_range,
            retro=retro,
            created_at=orm_model.created_at,
            updated_at=orm_model.updated_at,
        )

    def to_orm(self, aggregate: Sprint) -> SprintORM:
        # DateRange → две колонки
        sprint_start = aggregate.date_range.start if aggregate.date_range else None
        sprint_end = aggregate.date_range.end if aggregate.date_range else None

        # SprintGoal → строка
        goal = aggregate.goal.value if aggregate.goal else None

        orm = SprintORM(
            id=self._map_uuid(aggregate.id),
            project_id=self._map_uuid(aggregate.project_id),
            name=aggregate.name,
            goal=goal,
            status=aggregate.status.value,
            sprint_start=sprint_start,
            sprint_end=sprint_end,
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,
        )

        # SprintRetro (1:1)
        if aggregate.retro is not None:
            orm.retro = self._retro_to_orm(aggregate.retro, aggregate.id)

        return orm

    # --- SprintRetro helpers ---

    def _retro_orm_to_domain(self, orm: SprintRetroORM) -> SprintRetro:
        sections = [
            RetroSection(
                title=s["title"],
                prompt=s.get("prompt"),
                item_type=RetroItemType(s.get("item_type", "neutral")),
            )
            for s in orm.sections
        ]
        items = [self._retro_item_orm_to_domain(i) for i in orm.items]

        return SprintRetro(
            id=self._map_id(orm.id),
            template_name=orm.template_name,
            sections=sections,
            items=items,
            created_at=orm.created_at,
        )

    def _retro_to_orm(self, retro: SprintRetro, sprint_id: Id) -> SprintRetroORM:
        sections = [
            {
                "title": s.title,
                "prompt": s.prompt,
                "item_type": s.item_type.value,
            }
            for s in retro.sections
        ]

        orm = SprintRetroORM(
            id=self._map_uuid(retro.id),
            sprint_id=self._map_uuid(sprint_id),
            template_name=retro.template_name,
            sections=sections,
            created_at=retro.created_at,
        )
        orm.items = [self._retro_item_to_orm(i, retro.id) for i in retro.items]
        return orm

    # --- RetroItem helpers ---

    def _retro_item_orm_to_domain(self, orm: RetroItemORM) -> RetroItem:
        return RetroItem(
            id=self._map_id(orm.id),
            section_id=self._map_id(orm.section_id),
            content=orm.content,
            author_id=self._map_id(orm.author_id),
            votes=orm.votes,
            created_at=orm.created_at,
        )

    def _retro_item_to_orm(self, item: RetroItem, retro_id: Id) -> RetroItemORM:
        return RetroItemORM(
            id=self._map_uuid(item.id),
            retro_id=self._map_uuid(retro_id),
            section_id=self._map_uuid(item.section_id),
            content=item.content,
            author_id=self._map_uuid(item.author_id),
            votes=item.votes,
        )

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.domain.exceptions.entity_not_found_exception import EntityNotFoundException
from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.persistence.sqlalchemy_repository import SqlAlchemyRepository
from app.context.task.domain.aggregates.task_template import TaskTemplate
from app.context.task.domain.repositories.task_template_repository import TaskTemplateRepository
from app.context.task.domain.value_objects.label import Label
from app.context.task.infrastructure.persistence.mappers.task_template_mapper import TaskTemplateMapper
from app.context.task.infrastructure.persistence.orm_models.task_template_orm import (
    TemplateChecklistItemORM,
    TemplateChecklistORM,
    TaskTemplateORM,
    task_template_labels_table,
)


class SqlTaskTemplateRepository(SqlAlchemyRepository[TaskTemplate, TaskTemplateORM], TaskTemplateRepository):
    """SQLAlchemy-реализация TaskTemplateRepository."""

    def __init__(self, session: AsyncSession, mapper: TaskTemplateMapper) -> None:
        super().__init__(session=session, mapper=mapper, orm_model_class=TaskTemplateORM)

    # ------------------------------------------------------------------
    # Override add — labels через association table
    # ------------------------------------------------------------------

    async def add(self, aggregate: TaskTemplate) -> TaskTemplate:
        orm_model = self._mapper.to_orm(aggregate)
        self._session.add(orm_model)
        await self._session.flush()

        # Labels через association table
        for label in aggregate.default_labels:
            label_dict = self._mapper.label_to_dict(label)
            await self._session.execute(
                task_template_labels_table.insert().values(
                    template_id=orm_model.id,
                    label_name=label_dict["label_name"],
                    label_color=label_dict["label_color"],
                )
            )

        await self._session.flush()
        return aggregate

    # ------------------------------------------------------------------
    # Override update — синхронизация дочерних + labels
    # ------------------------------------------------------------------

    async def update(self, aggregate: TaskTemplate) -> TaskTemplate:
        uuid_val = self._mapper._map_uuid(aggregate.id)
        stmt = select(TaskTemplateORM).where(TaskTemplateORM.id == uuid_val)
        result = await self._session.execute(stmt)
        orm_model = result.scalar_one_or_none()
        if orm_model is None:
            raise EntityNotFoundException(entity_type="TaskTemplate", id=aggregate.id)

        # Обновить скалярные поля
        updated_orm = self._mapper.to_orm(aggregate)
        for column in TaskTemplateORM.__table__.columns:
            col_name = column.name
            if col_name in ("id", "created_at"):
                continue
            setattr(orm_model, col_name, getattr(updated_orm, col_name, None))

        # Синхронизация дочерних: delete old + insert new
        await self._session.execute(
            TemplateChecklistItemORM.__table__.delete().where(
                TemplateChecklistItemORM.checklist_id.in_(
                    select(TemplateChecklistORM.id).where(TemplateChecklistORM.template_id == uuid_val)
                )
            )
        )
        await self._session.execute(
            TemplateChecklistORM.__table__.delete().where(TemplateChecklistORM.template_id == uuid_val)
        )

        for checklist in aggregate.default_checklists:
            cl_orm = self._mapper._checklist_to_orm(checklist, aggregate.id)
            self._session.add(cl_orm)

        # Синхронизация labels
        await self._session.execute(
            task_template_labels_table.delete().where(task_template_labels_table.c.template_id == uuid_val)
        )
        for label in aggregate.default_labels:
            label_dict = self._mapper.label_to_dict(label)
            await self._session.execute(
                task_template_labels_table.insert().values(
                    template_id=uuid_val,
                    label_name=label_dict["label_name"],
                    label_color=label_dict["label_color"],
                )
            )

        await self._session.flush()
        return aggregate

    # ------------------------------------------------------------------
    # Helper: загрузить labels для ORM-объекта
    # ------------------------------------------------------------------

    async def _load_labels(self, orm_model: TaskTemplateORM) -> list[Label]:
        """Загрузить labels из association table и прикрепить к ORM."""
        stmt = select(task_template_labels_table).where(task_template_labels_table.c.template_id == orm_model.id)
        result = await self._session.execute(stmt)
        rows = result.fetchall()
        labels = [self._mapper.dict_to_label({"label_name": r.label_name, "label_color": r.label_color}) for r in rows]
        orm_model._loaded_labels = labels  # type: ignore[attr-defined]
        return labels

    async def _to_domain_with_labels(self, orm_model: TaskTemplateORM) -> TaskTemplate:
        """Преобразовать ORM → Domain с подгрузкой labels."""
        await self._load_labels(orm_model)
        return self._mapper.to_domain(orm_model)

    # ------------------------------------------------------------------
    # Override get_by_id — с подгрузкой labels
    # ------------------------------------------------------------------

    async def get_by_id(self, id: Id) -> TaskTemplate | None:
        uuid_value = self._mapper._map_uuid(id)
        stmt = select(TaskTemplateORM).where(TaskTemplateORM.id == uuid_value)
        result = await self._session.execute(stmt)
        orm_model = result.scalar_one_or_none()
        if orm_model is None:
            return None
        return await self._to_domain_with_labels(orm_model)

    # ------------------------------------------------------------------
    # Специфичные методы
    # ------------------------------------------------------------------

    async def get_by_project(self, project_id: Id) -> list[TaskTemplate]:
        # TaskTemplate не привязан к проекту — возвращаем все шаблоны
        # (системные глобальны, кастомные могут появиться позже)
        return await self.get_all()

    async def get_system_templates(self) -> list[TaskTemplate]:
        stmt = select(TaskTemplateORM).where(TaskTemplateORM.is_system.is_(True))
        result = await self._session.execute(stmt)
        templates = []
        for orm in result.scalars().all():
            templates.append(await self._to_domain_with_labels(orm))
        return templates

    async def get_by_name(self, name: str) -> TaskTemplate | None:
        stmt = select(TaskTemplateORM).where(TaskTemplateORM.name == name)
        result = await self._session.execute(stmt)
        orm_model = result.scalar_one_or_none()
        if orm_model is None:
            return None
        return await self._to_domain_with_labels(orm_model)

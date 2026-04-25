from __future__ import annotations

from app.shared.domain.value_objects.color_vo import Color
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.rich_text_format import RichTextFormat
from app.shared.domain.value_objects.rich_text_vo import RichText
from app.shared.infrastructure.persistence.sqlalchemy_base_mapper import BaseMapper

from app.context.task.domain.aggregates.task_template import TaskTemplate
from app.context.task.domain.entities.checklist import Checklist
from app.context.task.domain.entities.checklist_item import ChecklistItem
from app.context.task.domain.value_objects.label import Label
from app.context.task.domain.value_objects.task_type import TaskType
from app.context.task.infrastructure.persistence.orm_models.task_template_orm import (
    TaskTemplateORM,
    TemplateChecklistItemORM,
    TemplateChecklistORM,
)


class TaskTemplateMapper(BaseMapper[TaskTemplate, TaskTemplateORM]):
    """Data Mapper: TaskTemplate ↔ TaskTemplateORM."""

    # ------------------------------------------------------------------
    # ORM → Domain
    # ------------------------------------------------------------------

    def to_domain(self, orm_model: TaskTemplateORM) -> TaskTemplate:
        # RichText
        description: RichText | None = None
        if orm_model.description_content is not None:
            fmt = RichTextFormat(orm_model.description_format) if orm_model.description_format else RichTextFormat.MARKDOWN
            description = RichText(content=orm_model.description_content, format=fmt)

        # Labels — загружаются отдельно через association table в репозитории
        labels: list[Label] = getattr(orm_model, "_loaded_labels", [])

        # Дочерние сущности
        checklists = [self._checklist_to_domain(cl) for cl in orm_model.default_checklists]

        return TaskTemplate(
            id=self._map_id(orm_model.id),
            project_id=self._map_id(orm_model.project_id) if orm_model.project_id else None,
            name=orm_model.name,
            description=description,
            task_type=TaskType(orm_model.task_type),
            default_labels=labels,
            default_checklists=checklists,
            default_custom_fields=orm_model.default_custom_fields or {},
            is_system=orm_model.is_system,
            created_at=orm_model.created_at,
            updated_at=orm_model.updated_at,
        )

    # ------------------------------------------------------------------
    # Domain → ORM
    # ------------------------------------------------------------------

    def to_orm(self, aggregate: TaskTemplate) -> TaskTemplateORM:
        # RichText
        description_content = None
        description_format = None
        if aggregate.description is not None:
            description_content = aggregate.description.content
            description_format = aggregate.description.format.value

        orm = TaskTemplateORM(
            id=self._map_uuid(aggregate.id),
            project_id=self._map_uuid(aggregate.project_id) if aggregate.project_id else None,
            name=aggregate.name,
            description_content=description_content,
            description_format=description_format,
            task_type=aggregate.task_type.value,
            default_custom_fields=aggregate.default_custom_fields,
            is_system=aggregate.is_system,
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,
        )

        # Дочерние сущности
        orm.default_checklists = [self._checklist_to_orm(cl, aggregate.id) for cl in aggregate.default_checklists]

        return orm

    # ------------------------------------------------------------------
    # Checklist
    # ------------------------------------------------------------------

    def _checklist_to_domain(self, orm: TemplateChecklistORM) -> Checklist:
        items = [self._checklist_item_to_domain(i) for i in orm.items]
        return Checklist(
            id=self._map_id(orm.id),
            title=orm.title,
            items=items,
        )

    def _checklist_to_orm(self, checklist: Checklist, template_id: Id) -> TemplateChecklistORM:
        orm = TemplateChecklistORM(
            id=self._map_uuid(checklist.id),
            template_id=self._map_uuid(template_id),
            title=checklist.title,
        )
        orm.items = [self._checklist_item_to_orm(item, checklist.id) for item in checklist.items]
        return orm

    # ------------------------------------------------------------------
    # ChecklistItem
    # ------------------------------------------------------------------

    def _checklist_item_to_domain(self, orm: TemplateChecklistItemORM) -> ChecklistItem:
        return ChecklistItem(
            id=self._map_id(orm.id),
            text=orm.text,
            assignee_id=self._map_id(orm.assignee_id) if orm.assignee_id else None,
            due_date=orm.due_date,
            checked_at=orm.checked_at,
            order=orm.order,
        )

    def _checklist_item_to_orm(self, item: ChecklistItem, checklist_id: Id) -> TemplateChecklistItemORM:
        return TemplateChecklistItemORM(
            id=self._map_uuid(item.id),
            checklist_id=self._map_uuid(checklist_id),
            text=item.text,
            assignee_id=self._map_uuid(item.assignee_id) if item.assignee_id else None,
            due_date=item.due_date,
            checked_at=item.checked_at,
            order=item.order,
        )

    # ------------------------------------------------------------------
    # Label helpers (используются в репозитории)
    # ------------------------------------------------------------------

    def label_to_dict(self, label: Label) -> dict[str, str | None]:
        """Преобразовать Label в dict для association table insert."""
        return {
            "label_name": label.name,
            "label_color": str(label.color) if label.color else None,
        }

    def dict_to_label(self, data: dict) -> Label:
        """Преобразовать строку из association table в Label."""
        color = Color(data["label_color"]) if data.get("label_color") else None
        return Label(name=data["label_name"], color=color)

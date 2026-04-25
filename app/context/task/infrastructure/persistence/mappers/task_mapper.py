from __future__ import annotations

from app.shared.domain.value_objects.color_vo import Color
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.rich_text_format import RichTextFormat
from app.shared.domain.value_objects.rich_text_vo import RichText
from app.shared.infrastructure.persistence.sqlalchemy_base_mapper import BaseMapper

from app.context.task.domain.aggregates.task import Task
from app.context.task.domain.entities.checklist import Checklist
from app.context.task.domain.entities.checklist_item import ChecklistItem
from app.context.task.domain.entities.task_attachment import TaskAttachment
from app.context.task.domain.entities.task_relation import TaskRelation
from app.context.task.domain.entities.task_watcher import TaskWatcher
from app.context.task.domain.value_objects.actual_effort import ActualEffort
from app.context.task.domain.value_objects.effort_estimate import EffortEstimate
from app.context.task.domain.value_objects.effort_unit import EffortUnit
from app.context.task.domain.value_objects.label import Label
from app.context.task.domain.value_objects.recurrence_config import RecurrenceConfig
from app.context.task.domain.value_objects.recurrence_pattern import RecurrencePattern
from app.context.task.domain.value_objects.relation_type import RelationType
from app.context.task.domain.value_objects.task_order import TaskOrder
from app.context.task.domain.value_objects.task_priority import TaskPriority
from app.context.task.domain.value_objects.task_progress import TaskProgress
from app.context.task.domain.value_objects.task_status import TaskStatus
from app.context.task.domain.value_objects.task_type import TaskType
from app.context.task.infrastructure.persistence.orm_models.task_orm import (
    TaskAttachmentORM,
    TaskChecklistItemORM,
    TaskChecklistORM,
    TaskORM,
    TaskRelationORM,
    TaskWatcherORM,
)


class TaskMapper(BaseMapper[Task, TaskORM]):
    """Data Mapper: Task ↔ TaskORM."""

    # ------------------------------------------------------------------
    # ORM → Domain
    # ------------------------------------------------------------------

    def to_domain(self, orm_model: TaskORM) -> Task:
        # RichText
        description: RichText | None = None
        if orm_model.description_content is not None:
            fmt = RichTextFormat(orm_model.description_format) if orm_model.description_format else RichTextFormat.MARKDOWN
            description = RichText(content=orm_model.description_content, format=fmt)

        # Effort VO
        effort_estimate: EffortEstimate | None = None
        if orm_model.effort_estimate_value is not None:
            unit = EffortUnit(orm_model.effort_estimate_unit) if orm_model.effort_estimate_unit else EffortUnit.HOURS
            effort_estimate = EffortEstimate(value=orm_model.effort_estimate_value, unit=unit)

        actual_effort: ActualEffort | None = None
        if orm_model.actual_effort_value is not None:
            unit = EffortUnit(orm_model.actual_effort_unit) if orm_model.actual_effort_unit else EffortUnit.HOURS
            actual_effort = ActualEffort(value=orm_model.actual_effort_value, unit=unit)

        # TaskOrder
        order = TaskOrder(
            position=orm_model.order_position,
            column_id=self._map_id(orm_model.order_column_id),
        )

        # RecurrenceConfig
        recurrence: RecurrenceConfig | None = None
        if orm_model.recurrence_pattern is not None:
            recurrence = RecurrenceConfig(
                pattern=RecurrencePattern(orm_model.recurrence_pattern),
                interval=orm_model.recurrence_interval or 1,
                end_date=orm_model.recurrence_end_date,
                max_occurrences=orm_model.recurrence_max_occurrences,
            )

        # assignee_ids
        assignee_ids = [self._map_id(uid_str) for uid_str in (orm_model.assignee_ids or [])]

        # Labels — загружаются отдельно через association table в репозитории
        # (labels не хранятся в ORM relationship, а через task_labels_table)
        labels: list[Label] = getattr(orm_model, "_loaded_labels", [])

        # Дочерние сущности
        checklists = [self._checklist_to_domain(cl) for cl in orm_model.checklists]
        relations = [self._relation_to_domain(r) for r in orm_model.relations]
        watchers = [self._watcher_to_domain(w) for w in orm_model.watchers]
        attachments = [self._attachment_to_domain(a) for a in orm_model.attachments]

        return Task(
            id=self._map_id(orm_model.id),
            project_id=self._map_id(orm_model.project_id),
            parent_task_id=self._map_id(orm_model.parent_task_id) if orm_model.parent_task_id else None,
            epic_id=self._map_id(orm_model.epic_id) if orm_model.epic_id else None,
            title=orm_model.title,
            description=description,
            status_id=self._map_id(orm_model.status_id) if orm_model.status_id else None,
            priority=TaskPriority(orm_model.priority),
            task_type=TaskType(orm_model.task_type),
            assignee_ids=assignee_ids,
            reporter_id=self._map_id(orm_model.reporter_id) if orm_model.reporter_id else None,
            labels=labels,
            progress=TaskProgress(value=orm_model.progress),
            effort_estimate=effort_estimate,
            actual_effort=actual_effort,
            start_date=orm_model.start_date,
            due_date=orm_model.due_date,
            completed_at=orm_model.completed_at,
            custom_fields=orm_model.custom_fields or {},
            checklists=checklists,
            relations=relations,
            watchers=watchers,
            attachments=attachments,
            order=order,
            sprint_id=self._map_id(orm_model.sprint_id) if orm_model.sprint_id else None,
            status=TaskStatus(orm_model.status),
            recurrence=recurrence,
            created_at=orm_model.created_at,
            updated_at=orm_model.updated_at,
        )

    # ------------------------------------------------------------------
    # Domain → ORM
    # ------------------------------------------------------------------

    def to_orm(self, aggregate: Task) -> TaskORM:
        # RichText
        description_content = None
        description_format = None
        if aggregate.description is not None:
            description_content = aggregate.description.content
            description_format = aggregate.description.format.value

        # Effort VO
        effort_estimate_value = None
        effort_estimate_unit = None
        if aggregate.effort_estimate is not None:
            effort_estimate_value = aggregate.effort_estimate.value
            effort_estimate_unit = aggregate.effort_estimate.unit.value

        actual_effort_value = None
        actual_effort_unit = None
        if aggregate.actual_effort is not None:
            actual_effort_value = aggregate.actual_effort.value
            actual_effort_unit = aggregate.actual_effort.unit.value

        # RecurrenceConfig
        recurrence_pattern = None
        recurrence_interval = None
        recurrence_end_date = None
        recurrence_max_occurrences = None
        if aggregate.recurrence is not None:
            recurrence_pattern = aggregate.recurrence.pattern.value
            recurrence_interval = aggregate.recurrence.interval
            recurrence_end_date = aggregate.recurrence.end_date
            recurrence_max_occurrences = aggregate.recurrence.max_occurrences

        orm = TaskORM(
            id=self._map_uuid(aggregate.id),
            project_id=self._map_uuid(aggregate.project_id),
            parent_task_id=self._map_uuid(aggregate.parent_task_id) if aggregate.parent_task_id else None,
            epic_id=self._map_uuid(aggregate.epic_id) if aggregate.epic_id else None,
            title=aggregate.title,
            description_content=description_content,
            description_format=description_format,
            status_id=self._map_uuid(aggregate.status_id) if aggregate.status_id else None,
            priority=aggregate.priority.value,
            task_type=aggregate.task_type.value,
            assignee_ids=[str(self._map_uuid(uid)) for uid in aggregate.assignee_ids],
            reporter_id=self._map_uuid(aggregate.reporter_id) if aggregate.reporter_id else None,
            progress=aggregate.progress.value,
            effort_estimate_value=effort_estimate_value,
            effort_estimate_unit=effort_estimate_unit,
            actual_effort_value=actual_effort_value,
            actual_effort_unit=actual_effort_unit,
            start_date=aggregate.start_date,
            due_date=aggregate.due_date,
            completed_at=aggregate.completed_at,
            custom_fields=aggregate.custom_fields,
            order_position=aggregate.order.position,
            order_column_id=self._map_uuid(aggregate.order.column_id),
            sprint_id=self._map_uuid(aggregate.sprint_id) if aggregate.sprint_id else None,
            status=aggregate.status.value,
            recurrence_pattern=recurrence_pattern,
            recurrence_interval=recurrence_interval,
            recurrence_end_date=recurrence_end_date,
            recurrence_max_occurrences=recurrence_max_occurrences,
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,
        )

        # Дочерние сущности
        orm.checklists = [self._checklist_to_orm(cl, aggregate.id) for cl in aggregate.checklists]
        orm.relations = [self._relation_to_orm(r, aggregate.id) for r in aggregate.relations]
        orm.watchers = [self._watcher_to_orm(w, aggregate.id) for w in aggregate.watchers]
        orm.attachments = [self._attachment_to_orm(a, aggregate.id) for a in aggregate.attachments]

        return orm

    # ------------------------------------------------------------------
    # Checklist
    # ------------------------------------------------------------------

    def _checklist_to_domain(self, orm: TaskChecklistORM) -> Checklist:
        items = [self._checklist_item_to_domain(i) for i in orm.items]
        return Checklist(
            id=self._map_id(orm.id),
            title=orm.title,
            items=items,
        )

    def _checklist_to_orm(self, checklist: Checklist, task_id: Id) -> TaskChecklistORM:
        orm = TaskChecklistORM(
            id=self._map_uuid(checklist.id),
            task_id=self._map_uuid(task_id),
            title=checklist.title,
        )
        orm.items = [self._checklist_item_to_orm(item, checklist.id) for item in checklist.items]
        return orm

    # ------------------------------------------------------------------
    # ChecklistItem
    # ------------------------------------------------------------------

    def _checklist_item_to_domain(self, orm: TaskChecklistItemORM) -> ChecklistItem:
        return ChecklistItem(
            id=self._map_id(orm.id),
            text=orm.text,
            is_checked=orm.is_checked,
            assignee_id=self._map_id(orm.assignee_id) if orm.assignee_id else None,
            due_date=orm.due_date,
            checked_at=orm.checked_at,
            order=orm.order,
        )

    def _checklist_item_to_orm(self, item: ChecklistItem, checklist_id: Id) -> TaskChecklistItemORM:
        return TaskChecklistItemORM(
            id=self._map_uuid(item.id),
            checklist_id=self._map_uuid(checklist_id),
            text=item.text,
            is_checked=item.is_checked,
            assignee_id=self._map_uuid(item.assignee_id) if item.assignee_id else None,
            due_date=item.due_date,
            checked_at=item.checked_at,
            order=item.order,
        )

    # ------------------------------------------------------------------
    # TaskRelation
    # ------------------------------------------------------------------

    def _relation_to_domain(self, orm: TaskRelationORM) -> TaskRelation:
        return TaskRelation(
            id=self._map_id(orm.id),
            related_task_id=self._map_id(orm.related_task_id),
            relation_type=RelationType(orm.relation_type),
            created_at=orm.created_at_rel,
            created_by=self._map_id(orm.created_by),
        )

    def _relation_to_orm(self, relation: TaskRelation, task_id: Id) -> TaskRelationORM:
        return TaskRelationORM(
            id=self._map_uuid(relation.id),
            task_id=self._map_uuid(task_id),
            related_task_id=self._map_uuid(relation.related_task_id),
            relation_type=relation.relation_type.value,
            created_at_rel=relation.created_at,
            created_by=self._map_uuid(relation.created_by),
        )

    # ------------------------------------------------------------------
    # TaskWatcher
    # ------------------------------------------------------------------

    def _watcher_to_domain(self, orm: TaskWatcherORM) -> TaskWatcher:
        return TaskWatcher(
            id=self._map_id(orm.id),
            user_id=self._map_id(orm.user_id),
            watched_at=orm.watched_at,
        )

    def _watcher_to_orm(self, watcher: TaskWatcher, task_id: Id) -> TaskWatcherORM:
        return TaskWatcherORM(
            id=self._map_uuid(watcher.id),
            task_id=self._map_uuid(task_id),
            user_id=self._map_uuid(watcher.user_id),
            watched_at=watcher.watched_at,
        )

    # ------------------------------------------------------------------
    # TaskAttachment
    # ------------------------------------------------------------------

    def _attachment_to_domain(self, orm: TaskAttachmentORM) -> TaskAttachment:
        return TaskAttachment(
            id=self._map_id(orm.id),
            file_id=self._map_id(orm.file_id),
            filename=orm.filename,
            size_bytes=orm.size_bytes,
            uploaded_by=self._map_id(orm.uploaded_by),
            uploaded_at=orm.uploaded_at,
        )

    def _attachment_to_orm(self, attachment: TaskAttachment, task_id: Id) -> TaskAttachmentORM:
        return TaskAttachmentORM(
            id=self._map_uuid(attachment.id),
            task_id=self._map_uuid(task_id),
            file_id=self._map_uuid(attachment.file_id),
            filename=attachment.filename,
            size_bytes=attachment.size_bytes,
            uploaded_by=self._map_uuid(attachment.uploaded_by),
            uploaded_at=attachment.uploaded_at,
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

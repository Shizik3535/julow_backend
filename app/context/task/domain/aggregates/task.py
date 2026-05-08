from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone

from app.shared.domain.base_aggregate import AggregateRoot
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.rich_text_vo import RichText
from app.context.task.domain.value_objects.task_priority import TaskPriority
from app.context.task.domain.value_objects.task_type import TaskType
from app.context.task.domain.value_objects.task_status import TaskStatus
from app.context.task.domain.value_objects.task_progress import TaskProgress
from app.context.task.domain.value_objects.effort_estimate import EffortEstimate
from app.context.task.domain.value_objects.actual_effort import ActualEffort
from app.context.task.domain.value_objects.effort_unit import EffortUnit
from app.context.task.domain.value_objects.label import Label
from app.context.task.domain.value_objects.task_order import TaskOrder
from app.context.task.domain.value_objects.relation_type import RelationType
from app.context.task.domain.value_objects.recurrence_config import RecurrenceConfig
from app.context.task.domain.entities.checklist import Checklist
from app.context.task.domain.entities.checklist_item import ChecklistItem
from app.context.task.domain.entities.task_relation import TaskRelation
from app.context.task.domain.entities.task_watcher import TaskWatcher
from app.context.task.domain.entities.task_attachment import TaskAttachment
from app.context.task.domain.events.task_events import (
    TaskCreated,
    TaskInfoChanged,
    TaskArchived,
    TaskRestored,
    TaskDeleted,
    TaskStatusChanged,
    TaskAssigned,
    TaskUnassigned,
    TaskPriorityChanged,
    TaskTypeChanged,
    TaskMoved,
    TaskMovedToSprint,
    TaskRemovedFromSprint,
    TaskMovedToEpic,
    TaskRemovedFromEpic,
    ChecklistAdded,
    ChecklistRemoved,
    ChecklistItemAdded,
    ChecklistItemToggled,
    ChecklistItemAssigned,
    TaskRelationAdded,
    TaskRelationRemoved,
    TaskProgressUpdated,
    TaskEffortUpdated,
    TaskWatcherAdded,
    TaskWatcherRemoved,
    TaskAttachmentAdded,
    TaskAttachmentRemoved,
    TaskCustomFieldChanged,
)
from app.context.task.domain.exceptions.task_exceptions import (
    TaskArchivedException,
    CannotRelateTaskToSelfException,
    DuplicateRelationException,
    DuplicateWatcherException,
    DuplicateLabelException,
    EffortUnitMismatchException,
    ChecklistNotFoundException,
    ChecklistItemNotFoundException,
)


@dataclass
class Task(AggregateRoot):
    """
    Корень агрегата задачи (Task BC).

    Все ссылки на Project BC — opaque ID. Проверки валидности на app-слое.

    Атрибуты:
        project_id: Opaque ID проекта (из Project BC).
        parent_task_id: ID родительской задачи (иерархия).
        epic_id: Opaque ID эпика (из Epic AR).
        title: Заголовок задачи.
        description: Описание (форматированный текст).
        status_id: Opaque ID workflow-статуса (из Board AR).
        priority: Приоритет.
        task_type: Тип задачи.
        assignee_ids: Список ID исполнителей.
        reporter_id: ID автора задачи.
        labels: Список меток.
        progress: Прогресс (0–100).
        effort_estimate: Оценка усилия.
        actual_effort: Фактическое усилие.
        start_date: Дата начала.
        due_date: Дедлайн.
        completed_at: Время завершения.
        custom_fields: Значения кастомных полей.
        checklists: Список чек-листов.
        relations: Список связей.
        watchers: Список наблюдателей.
        attachments: Список вложений.
        order: Позиция на доске.
        sprint_id: Opaque ID спринта.
        status: Жизненный цикл задачи (ACTIVE/ARCHIVED/DELETED).
        recurrence: Конфигурация повторения.
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    project_id: Id | None = None
    parent_task_id: Id | None = None
    epic_id: Id | None = None
    title: str = ""
    description: RichText | None = None
    status_id: Id | None = None
    priority: TaskPriority = TaskPriority.NONE
    task_type: TaskType = TaskType.TASK
    assignee_ids: list[Id] = field(default_factory=list)
    reporter_id: Id | None = None
    labels: list[Label] = field(default_factory=list)
    progress: TaskProgress = field(default_factory=lambda: TaskProgress(value=0))
    effort_estimate: EffortEstimate | None = None
    actual_effort: ActualEffort | None = None
    start_date: date | None = None
    due_date: date | None = None
    completed_at: datetime | None = None
    custom_fields: dict[str, str] = field(default_factory=dict)
    checklists: list[Checklist] = field(default_factory=list)
    relations: list[TaskRelation] = field(default_factory=list)
    watchers: list[TaskWatcher] = field(default_factory=list)
    attachments: list[TaskAttachment] = field(default_factory=list)
    order: TaskOrder = field(default_factory=TaskOrder)
    sprint_id: Id | None = None
    status: TaskStatus = TaskStatus.ACTIVE
    recurrence: RecurrenceConfig | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    def __post_init__(self) -> None:
        """Валидация обязательных полей при прямом создании."""
        super().__post_init__()
        if not self.title:
            raise ValueError("title обязательное поле")
        if not self.project_id:
            raise ValueError("project_id обязательное поле")

    # --- Фабричные методы ---

    @classmethod
    def create(
        cls,
        title: str,
        project_id: Id,
        task_type: TaskType,
        reporter_id: Id,
        parent_task_id: Id | None = None,
        epic_id: Id | None = None,
    ) -> Task:
        """Создаёт задачу."""
        task = cls(
            title=title,
            project_id=project_id,
            task_type=task_type,
            reporter_id=reporter_id,
            parent_task_id=parent_task_id,
            epic_id=epic_id,
        )
        task._register_event(
            TaskCreated(
                task_id=str(task.id),
                project_id=str(project_id),
                title=title,
                task_type=task_type,
                parent_task_id=str(parent_task_id) if parent_task_id else "",
                epic_id=str(epic_id) if epic_id else "",
            )
        )
        return task

    @classmethod
    def create_from_template(
        cls,
        template_name: str,
        template_type: TaskType,
        template_labels: list[Label],
        template_checklists: list[Checklist],
        template_custom_fields: dict[str, str],
        project_id: Id,
        reporter_id: Id,
    ) -> Task:
        """Создаёт задачу из шаблона."""
        task = cls(
            title=template_name,
            project_id=project_id,
            task_type=template_type,
            reporter_id=reporter_id,
            labels=list(template_labels),
            checklists=list(template_checklists),
            custom_fields=dict(template_custom_fields),
        )
        task._register_event(
            TaskCreated(
                task_id=str(task.id),
                project_id=str(project_id),
                title=template_name,
                task_type=template_type,
            )
        )
        return task

    # --- Инварианты ---

    def _assert_can_modify(self) -> None:
        if self.status == TaskStatus.ARCHIVED:
            raise TaskArchivedException()
        if self.status == TaskStatus.DELETED:
            raise TaskArchivedException()

    # --- Информация ---

    def update_info(
        self,
        title: str | None = None,
        description: RichText | None = None,
        start_date: date | None = None,
        due_date: date | None = None,
    ) -> None:
        """Обновляет информацию задачи."""
        self._assert_can_modify()
        changed: list[str] = []
        if title is not None and self.title != title:
            self.title = title
            changed.append("title")
        if description is not None and self.description != description:
            self.description = description
            changed.append("description")
        if start_date is not None and self.start_date != start_date:
            self.start_date = start_date
            changed.append("start_date")
        if due_date is not None and self.due_date != due_date:
            self.due_date = due_date
            changed.append("due_date")
        if changed:
            self.updated_at = datetime.now(tz=timezone.utc)
            self._register_event(
                TaskInfoChanged(task_id=str(self.id), changed_fields=changed)
            )

    # --- Статус (workflow) ---

    def change_status(self, new_status_id: Id) -> None:
        """Изменяет workflow-статус. Проверка перехода на app-слое."""
        self._assert_can_modify()
        old_status_id = self.status_id
        self.status_id = new_status_id
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            TaskStatusChanged(
                task_id=str(self.id),
                old_status_id=str(old_status_id) if old_status_id else "",
                new_status_id=str(new_status_id),
            )
        )

    # --- Приоритет / Тип ---

    def change_priority(self, priority: TaskPriority) -> None:
        self._assert_can_modify()
        self.priority = priority
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            TaskPriorityChanged(task_id=str(self.id), new_priority=priority)
        )

    def change_type(self, task_type: TaskType) -> None:
        self._assert_can_modify()
        self.task_type = task_type
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            TaskTypeChanged(task_id=str(self.id), new_type=task_type)
        )

    # --- Исполнители ---

    def assign(self, user_id: Id) -> None:
        self._assert_can_modify()
        if user_id not in self.assignee_ids:
            self.assignee_ids.append(user_id)
            self.updated_at = datetime.now(tz=timezone.utc)
            self._register_event(
                TaskAssigned(task_id=str(self.id), assignee_id=str(user_id))
            )

    def unassign(self, user_id: Id) -> None:
        self._assert_can_modify()
        if user_id in self.assignee_ids:
            self.assignee_ids.remove(user_id)
            self.updated_at = datetime.now(tz=timezone.utc)
            self._register_event(
                TaskUnassigned(task_id=str(self.id), assignee_id=str(user_id))
            )

    # --- Прогресс ---

    def update_progress(self, progress: TaskProgress) -> None:
        self._assert_can_modify()
        self.progress = progress
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            TaskProgressUpdated(task_id=str(self.id), new_percent=progress.value)
        )

    def compute_progress_from_checklists(self) -> None:
        """Авто-вычисление прогресса из чек-листов."""
        total_items = sum(len(cl.items) for cl in self.checklists)
        if total_items == 0:
            return
        checked_items = sum(sum(1 for i in cl.items if i.is_checked) for cl in self.checklists)
        percent = int(checked_items / total_items * 100)
        self.update_progress(TaskProgress(value=percent))

    # --- Усилие ---

    def set_effort_estimate(self, estimate: EffortEstimate) -> None:
        self._assert_can_modify()
        if self.actual_effort is not None and self.actual_effort.unit != estimate.unit:
            raise EffortUnitMismatchException()
        self.effort_estimate = estimate
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            TaskEffortUpdated(task_id=str(self.id), changed_fields=["effort_estimate"])
        )

    def set_actual_effort(self, effort: ActualEffort) -> None:
        self._assert_can_modify()
        if self.effort_estimate is not None and self.effort_estimate.unit != effort.unit:
            raise EffortUnitMismatchException()
        self.actual_effort = effort
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            TaskEffortUpdated(task_id=str(self.id), changed_fields=["actual_effort"])
        )

    # --- Метки ---

    def add_label(self, label: Label) -> None:
        self._assert_can_modify()
        if any(l.name == label.name for l in self.labels):
            raise DuplicateLabelException(name=label.name)
        self.labels.append(label)
        self.updated_at = datetime.now(tz=timezone.utc)

    def remove_label(self, label_name: str) -> None:
        self._assert_can_modify()
        self.labels = [l for l in self.labels if l.name != label_name]
        self.updated_at = datetime.now(tz=timezone.utc)

    # --- Перемещение ---

    def move(self, column_id: Id, position: float) -> None:
        self._assert_can_modify()
        self.order = TaskOrder(position=position, column_id=column_id)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            TaskMoved(task_id=str(self.id), new_column_id=str(column_id), new_position=position)
        )

    # --- Жизненный цикл ---

    def archive(self) -> None:
        if self.status != TaskStatus.ACTIVE:
            return
        self.status = TaskStatus.ARCHIVED
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(TaskArchived(task_id=str(self.id)))

    def restore(self) -> None:
        if self.status != TaskStatus.ARCHIVED:
            return
        self.status = TaskStatus.ACTIVE
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(TaskRestored(task_id=str(self.id)))

    def soft_delete(self) -> None:
        self._assert_can_modify()
        self.status = TaskStatus.DELETED
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(TaskDeleted(task_id=str(self.id)))

    # --- Связи ---

    def add_relation(self, related_task_id: Id, relation_type: RelationType, created_by: Id) -> None:
        self._assert_can_modify()
        if related_task_id == self.id:
            raise CannotRelateTaskToSelfException()
        if any(r.related_task_id == related_task_id and r.relation_type == relation_type for r in self.relations):
            raise DuplicateRelationException()
        relation = TaskRelation(
            related_task_id=related_task_id,
            relation_type=relation_type,
            created_by=created_by,
        )
        self.relations.append(relation)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            TaskRelationAdded(
                task_id=str(self.id),
                related_task_id=str(related_task_id),
                relation_type=relation_type.value,
            )
        )

    def remove_relation(self, related_task_id: Id, relation_type: RelationType) -> None:
        self._assert_can_modify()
        self.relations = [
            r for r in self.relations
            if not (r.related_task_id == related_task_id and r.relation_type == relation_type)
        ]
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            TaskRelationRemoved(
                task_id=str(self.id),
                related_task_id=str(related_task_id),
                relation_type=relation_type.value,
            )
        )

    # --- Чек-листы ---

    def add_checklist(self, title: str) -> Checklist:
        self._assert_can_modify()
        checklist = Checklist(title=title)
        self.checklists.append(checklist)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            ChecklistAdded(task_id=str(self.id), checklist_id=str(checklist.id))
        )
        return checklist

    def remove_checklist(self, checklist_id: Id) -> None:
        self._assert_can_modify()
        checklist = next((cl for cl in self.checklists if cl.id == checklist_id), None)
        if checklist is None:
            raise ChecklistNotFoundException(id=checklist_id)
        self.checklists.remove(checklist)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            ChecklistRemoved(task_id=str(self.id), checklist_id=str(checklist_id))
        )

    def add_checklist_item(self, checklist_id: Id, text: str, assignee_id: Id | None = None, due_date: date | None = None) -> ChecklistItem:
        self._assert_can_modify()
        checklist = next((cl for cl in self.checklists if cl.id == checklist_id), None)
        if checklist is None:
            raise ChecklistNotFoundException(id=checklist_id)
        order = len(checklist.items)
        item = ChecklistItem(text=text, assignee_id=assignee_id, due_date=due_date, order=order)
        checklist.items.append(item)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            ChecklistItemAdded(task_id=str(self.id), checklist_id=str(checklist_id))
        )
        return item

    def toggle_checklist_item(self, checklist_id: Id, item_id: Id) -> None:
        self._assert_can_modify()
        checklist = next((cl for cl in self.checklists if cl.id == checklist_id), None)
        if checklist is None:
            raise ChecklistNotFoundException(id=checklist_id)
        item = next((i for i in checklist.items if i.id == item_id), None)
        if item is None:
            raise ChecklistItemNotFoundException(id=item_id)
        item.is_checked = not item.is_checked
        item.checked_at = datetime.now(tz=timezone.utc) if item.is_checked else None
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            ChecklistItemToggled(task_id=str(self.id), checklist_id=str(checklist_id), item_id=str(item_id))
        )

    def assign_checklist_item(self, checklist_id: Id, item_id: Id, assignee_id: Id) -> None:
        self._assert_can_modify()
        checklist = next((cl for cl in self.checklists if cl.id == checklist_id), None)
        if checklist is None:
            raise ChecklistNotFoundException(id=checklist_id)
        item = next((i for i in checklist.items if i.id == item_id), None)
        if item is None:
            raise ChecklistItemNotFoundException(id=item_id)
        item.assignee_id = assignee_id
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            ChecklistItemAssigned(task_id=str(self.id), checklist_id=str(checklist_id), assignee_id=str(assignee_id))
        )

    # --- Спринт / Эпик ---

    def assign_to_sprint(self, sprint_id: Id) -> None:
        self._assert_can_modify()
        self.sprint_id = sprint_id
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            TaskMovedToSprint(task_id=str(self.id), sprint_id=str(sprint_id))
        )

    def remove_from_sprint(self) -> None:
        self._assert_can_modify()
        self.sprint_id = None
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(TaskRemovedFromSprint(task_id=str(self.id)))

    def assign_to_epic(self, epic_id: Id) -> None:
        self._assert_can_modify()
        self.epic_id = epic_id
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            TaskMovedToEpic(task_id=str(self.id), epic_id=str(epic_id))
        )

    def remove_from_epic(self) -> None:
        self._assert_can_modify()
        self.epic_id = None
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(TaskRemovedFromEpic(task_id=str(self.id)))

    # --- Наблюдатели ---

    def add_watcher(self, user_id: Id) -> None:
        self._assert_can_modify()
        if any(w.user_id == user_id for w in self.watchers):
            raise DuplicateWatcherException(user_id=str(user_id))
        watcher = TaskWatcher(user_id=user_id)
        self.watchers.append(watcher)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            TaskWatcherAdded(task_id=str(self.id), user_id=str(user_id))
        )

    def remove_watcher(self, user_id: Id) -> None:
        self._assert_can_modify()
        self.watchers = [w for w in self.watchers if w.user_id != user_id]
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            TaskWatcherRemoved(task_id=str(self.id), user_id=str(user_id))
        )

    # --- Вложения ---

    def add_attachment(self, file_id: Id, filename: str, size_bytes: int, uploaded_by: Id) -> None:
        self._assert_can_modify()
        attachment = TaskAttachment(file_id=file_id, filename=filename, size_bytes=size_bytes, uploaded_by=uploaded_by)
        self.attachments.append(attachment)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            TaskAttachmentAdded(task_id=str(self.id), file_id=str(file_id))
        )

    def remove_attachment(self, file_id: Id) -> None:
        self._assert_can_modify()
        self.attachments = [a for a in self.attachments if a.file_id != file_id]
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            TaskAttachmentRemoved(task_id=str(self.id), file_id=str(file_id))
        )

    # --- Кастомные поля ---

    def set_custom_field(self, field_name: str, value: str) -> None:
        self._assert_can_modify()
        old_value = self.custom_fields.get(field_name)
        self.custom_fields[field_name] = value
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            TaskCustomFieldChanged(
                task_id=str(self.id),
                field_name=field_name,
                old_value=old_value or "",
                new_value=value,
            )
        )

    def remove_custom_field(self, field_name: str) -> None:
        self._assert_can_modify()
        if field_name in self.custom_fields:
            old_value = self.custom_fields.pop(field_name)
            self.updated_at = datetime.now(tz=timezone.utc)
            self._register_event(
                TaskCustomFieldChanged(
                    task_id=str(self.id),
                    field_name=field_name,
                    old_value=old_value,
                    new_value="",
                )
            )

    # --- Повторение ---

    def set_recurrence(self, config: RecurrenceConfig) -> None:
        self._assert_can_modify()
        self.recurrence = config
        self.updated_at = datetime.now(tz=timezone.utc)

    def remove_recurrence(self) -> None:
        self._assert_can_modify()
        self.recurrence = None
        self.updated_at = datetime.now(tz=timezone.utc)

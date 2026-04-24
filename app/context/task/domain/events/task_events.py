from __future__ import annotations

from dataclasses import dataclass, field

from app.shared.domain.base_domain_event import BaseDomainEvent
from app.context.task.domain.value_objects.task_priority import TaskPriority
from app.context.task.domain.value_objects.task_type import TaskType


@dataclass(frozen=True)
class TaskCreated(BaseDomainEvent):
    """Задача создана."""

    task_id: str = ""
    project_id: str = ""
    title: str = ""
    task_type: TaskType = TaskType.TASK
    parent_task_id: str = ""
    epic_id: str = ""


@dataclass(frozen=True)
class TaskInfoChanged(BaseDomainEvent):
    """Информация задачи обновлена."""

    task_id: str = ""
    changed_fields: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class TaskArchived(BaseDomainEvent):
    """Задача архивирована."""

    task_id: str = ""


@dataclass(frozen=True)
class TaskRestored(BaseDomainEvent):
    """Задача восстановлена."""

    task_id: str = ""


@dataclass(frozen=True)
class TaskDeleted(BaseDomainEvent):
    """Задача удалена (soft delete)."""

    task_id: str = ""


@dataclass(frozen=True)
class TaskStatusChanged(BaseDomainEvent):
    """Workflow статус изменён."""

    task_id: str = ""
    old_status_id: str = ""
    new_status_id: str = ""


@dataclass(frozen=True)
class TaskAssigned(BaseDomainEvent):
    """Исполнитель назначен."""

    task_id: str = ""
    assignee_id: str = ""


@dataclass(frozen=True)
class TaskUnassigned(BaseDomainEvent):
    """Исполнитель снят."""

    task_id: str = ""
    assignee_id: str = ""


@dataclass(frozen=True)
class TaskPriorityChanged(BaseDomainEvent):
    """Приоритет изменён."""

    task_id: str = ""
    new_priority: TaskPriority = TaskPriority.NONE


@dataclass(frozen=True)
class TaskTypeChanged(BaseDomainEvent):
    """Тип изменён."""

    task_id: str = ""
    new_type: TaskType = TaskType.TASK


@dataclass(frozen=True)
class TaskMoved(BaseDomainEvent):
    """Задача перемещена (drag-n-drop)."""

    task_id: str = ""
    new_column_id: str = ""
    new_position: float = 0.0


@dataclass(frozen=True)
class TaskMovedToSprint(BaseDomainEvent):
    """Задача назначена на спринт."""

    task_id: str = ""
    sprint_id: str = ""


@dataclass(frozen=True)
class TaskRemovedFromSprint(BaseDomainEvent):
    """Задача убрана из спринта."""

    task_id: str = ""


@dataclass(frozen=True)
class TaskMovedToEpic(BaseDomainEvent):
    """Задача привязана к эпику."""

    task_id: str = ""
    epic_id: str = ""


@dataclass(frozen=True)
class TaskRemovedFromEpic(BaseDomainEvent):
    """Задача отвязана от эпика."""

    task_id: str = ""


@dataclass(frozen=True)
class BulkTasksUpdated(BaseDomainEvent):
    """Массовое обновление задач."""

    task_ids: list[str] = field(default_factory=list)
    changes: dict = field(default_factory=dict)


@dataclass(frozen=True)
class ChecklistAdded(BaseDomainEvent):
    """Чек-лист добавлен."""

    task_id: str = ""
    checklist_id: str = ""


@dataclass(frozen=True)
class ChecklistRemoved(BaseDomainEvent):
    """Чек-лист удалён."""

    task_id: str = ""
    checklist_id: str = ""


@dataclass(frozen=True)
class ChecklistItemAdded(BaseDomainEvent):
    """Пункт чек-листа добавлен."""

    task_id: str = ""
    checklist_id: str = ""


@dataclass(frozen=True)
class ChecklistItemToggled(BaseDomainEvent):
    """Пункт чек-листа отмечен/снят."""

    task_id: str = ""
    checklist_id: str = ""
    item_id: str = ""


@dataclass(frozen=True)
class ChecklistItemAssigned(BaseDomainEvent):
    """Исполнитель назначен на пункт чек-листа."""

    task_id: str = ""
    checklist_id: str = ""
    assignee_id: str = ""


@dataclass(frozen=True)
class TaskRelationAdded(BaseDomainEvent):
    """Связь добавлена."""

    task_id: str = ""
    related_task_id: str = ""
    relation_type: str = ""


@dataclass(frozen=True)
class TaskRelationRemoved(BaseDomainEvent):
    """Связь удалена."""

    task_id: str = ""
    related_task_id: str = ""
    relation_type: str = ""


@dataclass(frozen=True)
class TaskProgressUpdated(BaseDomainEvent):
    """Прогресс обновлён."""

    task_id: str = ""
    new_percent: int = 0


@dataclass(frozen=True)
class TaskEffortUpdated(BaseDomainEvent):
    """Оценка/фактическое усилие обновлено."""

    task_id: str = ""
    changed_fields: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class TaskWatcherAdded(BaseDomainEvent):
    """Наблюдатель добавлен."""

    task_id: str = ""
    user_id: str = ""


@dataclass(frozen=True)
class TaskWatcherRemoved(BaseDomainEvent):
    """Наблюдатель удалён."""

    task_id: str = ""
    user_id: str = ""


@dataclass(frozen=True)
class TaskAttachmentAdded(BaseDomainEvent):
    """Вложение добавлено."""

    task_id: str = ""
    file_id: str = ""


@dataclass(frozen=True)
class TaskAttachmentRemoved(BaseDomainEvent):
    """Вложение удалено."""

    task_id: str = ""
    file_id: str = ""


@dataclass(frozen=True)
class TaskCustomFieldChanged(BaseDomainEvent):
    """Кастомное поле изменено."""

    task_id: str = ""
    field_name: str = ""
    old_value: str = ""
    new_value: str = ""


@dataclass(frozen=True)
class TaskDeadlineApproaching(BaseDomainEvent):
    """Дедлайн приближается."""

    task_id: str = ""
    due_date: str = ""


@dataclass(frozen=True)
class TaskOverdue(BaseDomainEvent):
    """Задача просрочена."""

    task_id: str = ""
    due_date: str = ""


@dataclass(frozen=True)
class RecurringTaskCreated(BaseDomainEvent):
    """Повторяющаяся задача создана."""

    source_task_id: str = ""
    new_task_id: str = ""


@dataclass(frozen=True)
class TaskCommentAdded(BaseDomainEvent):
    """Комментарий добавлен (opaque ID из Communication BC)."""

    task_id: str = ""
    comment_id: str = ""

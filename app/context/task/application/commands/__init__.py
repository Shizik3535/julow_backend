# --- Task AR ---
from app.context.task.application.commands.create_task import (
    CreateTaskCommand,
    CreateTaskHandler,
)
from app.context.task.application.commands.create_task_from_template import (
    CreateTaskFromTemplateCommand,
    CreateTaskFromTemplateHandler,
)
from app.context.task.application.commands.update_task_info import (
    UpdateTaskInfoCommand,
    UpdateTaskInfoHandler,
)
from app.context.task.application.commands.change_task_status import (
    ChangeTaskStatusCommand,
    ChangeTaskStatusHandler,
)
from app.context.task.application.commands.change_task_priority import (
    ChangeTaskPriorityCommand,
    ChangeTaskPriorityHandler,
)
from app.context.task.application.commands.change_task_type import (
    ChangeTaskTypeCommand,
    ChangeTaskTypeHandler,
)
from app.context.task.application.commands.assign_task import (
    AssignTaskCommand,
    AssignTaskHandler,
)
from app.context.task.application.commands.unassign_task import (
    UnassignTaskCommand,
    UnassignTaskHandler,
)
from app.context.task.application.commands.update_task_progress import (
    UpdateTaskProgressCommand,
    UpdateTaskProgressHandler,
)
from app.context.task.application.commands.compute_task_progress import (
    ComputeTaskProgressCommand,
    ComputeTaskProgressHandler,
)
from app.context.task.application.commands.set_effort_estimate import (
    SetEffortEstimateCommand,
    SetEffortEstimateHandler,
)
from app.context.task.application.commands.set_actual_effort import (
    SetActualEffortCommand,
    SetActualEffortHandler,
)
from app.context.task.application.commands.add_task_label import (
    AddTaskLabelCommand,
    AddTaskLabelHandler,
)
from app.context.task.application.commands.remove_task_label import (
    RemoveTaskLabelCommand,
    RemoveTaskLabelHandler,
)
from app.context.task.application.commands.move_task import (
    MoveTaskCommand,
    MoveTaskHandler,
)
from app.context.task.application.commands.archive_task import (
    ArchiveTaskCommand,
    ArchiveTaskHandler,
)
from app.context.task.application.commands.restore_task import (
    RestoreTaskCommand,
    RestoreTaskHandler,
)
from app.context.task.application.commands.delete_task import (
    DeleteTaskCommand,
    DeleteTaskHandler,
)
from app.context.task.application.commands.add_task_relation import (
    AddTaskRelationCommand,
    AddTaskRelationHandler,
)
from app.context.task.application.commands.remove_task_relation import (
    RemoveTaskRelationCommand,
    RemoveTaskRelationHandler,
)
from app.context.task.application.commands.add_checklist import (
    AddChecklistCommand,
    AddChecklistHandler,
)
from app.context.task.application.commands.remove_checklist import (
    RemoveChecklistCommand,
    RemoveChecklistHandler,
)
from app.context.task.application.commands.add_checklist_item import (
    AddChecklistItemCommand,
    AddChecklistItemHandler,
)
from app.context.task.application.commands.toggle_checklist_item import (
    ToggleChecklistItemCommand,
    ToggleChecklistItemHandler,
)
from app.context.task.application.commands.assign_checklist_item import (
    AssignChecklistItemCommand,
    AssignChecklistItemHandler,
)
from app.context.task.application.commands.assign_task_to_sprint import (
    AssignTaskToSprintCommand,
    AssignTaskToSprintHandler,
)
from app.context.task.application.commands.remove_task_from_sprint import (
    RemoveTaskFromSprintCommand,
    RemoveTaskFromSprintHandler,
)
from app.context.task.application.commands.assign_task_to_epic import (
    AssignTaskToEpicCommand,
    AssignTaskToEpicHandler,
)
from app.context.task.application.commands.remove_task_from_epic import (
    RemoveTaskFromEpicCommand,
    RemoveTaskFromEpicHandler,
)
from app.context.task.application.commands.add_task_watcher import (
    AddTaskWatcherCommand,
    AddTaskWatcherHandler,
)
from app.context.task.application.commands.remove_task_watcher import (
    RemoveTaskWatcherCommand,
    RemoveTaskWatcherHandler,
)
from app.context.task.application.commands.add_task_attachment import (
    AddTaskAttachmentCommand,
    AddTaskAttachmentHandler,
)
from app.context.task.application.commands.remove_task_attachment import (
    RemoveTaskAttachmentCommand,
    RemoveTaskAttachmentHandler,
)
from app.context.task.application.commands.set_task_custom_field import (
    SetTaskCustomFieldCommand,
    SetTaskCustomFieldHandler,
)
from app.context.task.application.commands.remove_task_custom_field import (
    RemoveTaskCustomFieldCommand,
    RemoveTaskCustomFieldHandler,
)
from app.context.task.application.commands.set_task_recurrence import (
    SetTaskRecurrenceCommand,
    SetTaskRecurrenceHandler,
)
from app.context.task.application.commands.remove_task_recurrence import (
    RemoveTaskRecurrenceCommand,
    RemoveTaskRecurrenceHandler,
)
from app.context.task.application.commands.bulk_update_tasks import (
    BulkUpdateTasksCommand,
    BulkUpdateTasksHandler,
)

# --- TaskTemplate AR ---
from app.context.task.application.commands.create_task_template import (
    CreateTaskTemplateCommand,
    CreateTaskTemplateHandler,
)
from app.context.task.application.commands.update_task_template import (
    UpdateTaskTemplateCommand,
    UpdateTaskTemplateHandler,
)
from app.context.task.application.commands.delete_task_template import (
    DeleteTaskTemplateCommand,
    DeleteTaskTemplateHandler,
)

__all__ = [
    # Task AR
    "CreateTaskCommand",
    "CreateTaskHandler",
    "CreateTaskFromTemplateCommand",
    "CreateTaskFromTemplateHandler",
    "UpdateTaskInfoCommand",
    "UpdateTaskInfoHandler",
    "ChangeTaskStatusCommand",
    "ChangeTaskStatusHandler",
    "ChangeTaskPriorityCommand",
    "ChangeTaskPriorityHandler",
    "ChangeTaskTypeCommand",
    "ChangeTaskTypeHandler",
    "AssignTaskCommand",
    "AssignTaskHandler",
    "UnassignTaskCommand",
    "UnassignTaskHandler",
    "UpdateTaskProgressCommand",
    "UpdateTaskProgressHandler",
    "ComputeTaskProgressCommand",
    "ComputeTaskProgressHandler",
    "SetEffortEstimateCommand",
    "SetEffortEstimateHandler",
    "SetActualEffortCommand",
    "SetActualEffortHandler",
    "AddTaskLabelCommand",
    "AddTaskLabelHandler",
    "RemoveTaskLabelCommand",
    "RemoveTaskLabelHandler",
    "MoveTaskCommand",
    "MoveTaskHandler",
    "ArchiveTaskCommand",
    "ArchiveTaskHandler",
    "RestoreTaskCommand",
    "RestoreTaskHandler",
    "DeleteTaskCommand",
    "DeleteTaskHandler",
    "AddTaskRelationCommand",
    "AddTaskRelationHandler",
    "RemoveTaskRelationCommand",
    "RemoveTaskRelationHandler",
    "AddChecklistCommand",
    "AddChecklistHandler",
    "RemoveChecklistCommand",
    "RemoveChecklistHandler",
    "AddChecklistItemCommand",
    "AddChecklistItemHandler",
    "ToggleChecklistItemCommand",
    "ToggleChecklistItemHandler",
    "AssignChecklistItemCommand",
    "AssignChecklistItemHandler",
    "AssignTaskToSprintCommand",
    "AssignTaskToSprintHandler",
    "RemoveTaskFromSprintCommand",
    "RemoveTaskFromSprintHandler",
    "AssignTaskToEpicCommand",
    "AssignTaskToEpicHandler",
    "RemoveTaskFromEpicCommand",
    "RemoveTaskFromEpicHandler",
    "AddTaskWatcherCommand",
    "AddTaskWatcherHandler",
    "RemoveTaskWatcherCommand",
    "RemoveTaskWatcherHandler",
    "AddTaskAttachmentCommand",
    "AddTaskAttachmentHandler",
    "RemoveTaskAttachmentCommand",
    "RemoveTaskAttachmentHandler",
    "SetTaskCustomFieldCommand",
    "SetTaskCustomFieldHandler",
    "RemoveTaskCustomFieldCommand",
    "RemoveTaskCustomFieldHandler",
    "SetTaskRecurrenceCommand",
    "SetTaskRecurrenceHandler",
    "RemoveTaskRecurrenceCommand",
    "RemoveTaskRecurrenceHandler",
    "BulkUpdateTasksCommand",
    "BulkUpdateTasksHandler",
    # TaskTemplate AR
    "CreateTaskTemplateCommand",
    "CreateTaskTemplateHandler",
    "UpdateTaskTemplateCommand",
    "UpdateTaskTemplateHandler",
    "DeleteTaskTemplateCommand",
    "DeleteTaskTemplateHandler",
]

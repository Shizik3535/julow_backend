from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.exceptions.task_app_exceptions import (
    TaskSprintNotAvailableException,
    TaskEpicNotAvailableException,
    TaskStatusTransitionNotAllowedException,
)
from app.context.task.application.ports.authorization.task_permission_checker_port import (
    TaskPermissionCheckerPort,
)
from app.context.task.application.ports.integration.inboard.board_port import BoardPort
from app.context.task.application.ports.integration.inboard.epic_port import EpicPort
from app.context.task.application.ports.integration.inboard.sprint_port import SprintPort
from app.context.task.domain.aggregates.changelog import ChangelogEntry
from app.context.task.domain.exceptions.task_exceptions import TaskNotFoundException
from app.context.task.domain.events.task_events import BulkTasksUpdated
from app.context.task.domain.repositories.changelog_repository import ChangelogRepository
from app.context.task.domain.repositories.task_repository import TaskRepository
from app.context.task.domain.value_objects.task_priority import TaskPriority


class BulkUpdateTasksCommand(BaseCommand):
    """
    Команда массового обновления задач.

    Атрибуты:
        task_ids: Список ID задач.
        changes: Словарь изменений (field → value).
        changed_by: ID изменившего.
    """

    task_ids: list[str]
    changes: dict[str, str]
    changed_by: str


class BulkUpdateTasksHandler(BaseCommandHandler[BulkUpdateTasksCommand, None]):
    """
    Обработчик массового обновления задач.

    Поддерживает: status_id, priority, sprint_id, epic_id.
    """

    REQUIRED_PERMISSION = "tasks.update"

    def __init__(
        self,
        task_repo: TaskRepository,
        changelog_repo: ChangelogRepository,
        board_port: BoardPort,
        sprint_port: SprintPort,
        epic_port: EpicPort,
        permission_checker: TaskPermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._task_repo = task_repo
        self._changelog_repo = changelog_repo
        self._board_port = board_port
        self._sprint_port = sprint_port
        self._epic_port = epic_port
        self._permission_checker = permission_checker
        self._event_bus = event_bus

    async def handle(self, command: BulkUpdateTasksCommand) -> None:
        if "sprint_id" in command.changes:
            sprint_id = command.changes["sprint_id"]
            if not await self._sprint_port.sprint_exists(sprint_id):
                raise TaskSprintNotAvailableException(sprint_id, "спринт не найден")

        if "epic_id" in command.changes:
            epic_id = command.changes["epic_id"]
            if not await self._epic_port.epic_exists(epic_id):
                raise TaskEpicNotAvailableException(epic_id, "эпик не найден")

        changed_by = Id.from_string(command.changed_by)

        checked_projects: set[str] = set()
        for task_id_str in command.task_ids:
            task = await self._task_repo.get_by_id(Id.from_string(task_id_str))
            if task is None:
                raise TaskNotFoundException(id=task_id_str)

            project_id_str = str(task.project_id)
            if project_id_str not in checked_projects:
                await self._permission_checker.require_permission(
                    user_id=command.changed_by,
                    project_id=project_id_str,
                    permission=self.REQUIRED_PERMISSION,
                )
                checked_projects.add(project_id_str)

            task_id = Id.from_string(task_id_str)

            if "status_id" in command.changes:
                new_status = command.changes["status_id"]
                old_status = str(task.status_id) if task.status_id else ""
                if task.status_id:
                    allowed = await self._board_port.is_transition_allowed(
                        str(task.project_id), old_status, new_status,
                    )
                    if not allowed:
                        raise TaskStatusTransitionNotAllowedException(old_status, new_status)
                task.change_status(Id.from_string(new_status))
                entry = ChangelogEntry.create(task_id=task_id, field_name="status_id", old_value=old_status, new_value=new_status, changed_by=changed_by)
                await self._changelog_repo.add(entry)

            if "priority" in command.changes:
                old_priority = task.priority.value
                task.change_priority(TaskPriority(command.changes["priority"]))
                entry = ChangelogEntry.create(task_id=task_id, field_name="priority", old_value=old_priority, new_value=command.changes["priority"], changed_by=changed_by)
                await self._changelog_repo.add(entry)

            if "sprint_id" in command.changes:
                old_sprint = str(task.sprint_id) if task.sprint_id else None
                task.assign_to_sprint(Id.from_string(command.changes["sprint_id"]))
                entry = ChangelogEntry.create(task_id=task_id, field_name="sprint_id", old_value=old_sprint, new_value=command.changes["sprint_id"], changed_by=changed_by)
                await self._changelog_repo.add(entry)

            if "epic_id" in command.changes:
                old_epic = str(task.epic_id) if task.epic_id else None
                task.assign_to_epic(Id.from_string(command.changes["epic_id"]))
                entry = ChangelogEntry.create(task_id=task_id, field_name="epic_id", old_value=old_epic, new_value=command.changes["epic_id"], changed_by=changed_by)
                await self._changelog_repo.add(entry)

            await self._task_repo.update(task)
            await self._event_bus.publish_all(task.clear_domain_events())

        await self._event_bus.publish_all([
            BulkTasksUpdated(task_ids=command.task_ids, changes=command.changes)
        ])

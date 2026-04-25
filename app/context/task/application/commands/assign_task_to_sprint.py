from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.exceptions.task_app_exceptions import TaskSprintNotAvailableException
from app.context.task.application.ports.authorization.task_permission_checker_port import (
    TaskPermissionCheckerPort,
)
from app.context.task.application.ports.integration.inboard.sprint_port import SprintPort
from app.context.task.domain.aggregates.changelog import ChangelogEntry
from app.context.task.domain.exceptions.task_exceptions import TaskNotFoundException
from app.context.task.domain.repositories.changelog_repository import ChangelogRepository
from app.context.task.domain.repositories.task_repository import TaskRepository


class AssignTaskToSprintCommand(BaseCommand):
    """
    Команда назначения задачи в спринт.

    Атрибуты:
        task_id: ID задачи.
        sprint_id: ID спринта.
        changed_by: ID изменившего.
    """

    task_id: str
    sprint_id: str
    changed_by: str


class AssignTaskToSprintHandler(BaseCommandHandler[AssignTaskToSprintCommand, None]):
    """
    Обработчик назначения задачи в спринт.

    Проверяет существование и доступность спринта через SprintPort.
    """

    REQUIRED_PERMISSION = "tasks.update"

    def __init__(
        self,
        task_repo: TaskRepository,
        changelog_repo: ChangelogRepository,
        sprint_port: SprintPort,
        permission_checker: TaskPermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._task_repo = task_repo
        self._changelog_repo = changelog_repo
        self._sprint_port = sprint_port
        self._permission_checker = permission_checker
        self._event_bus = event_bus

    async def handle(self, command: AssignTaskToSprintCommand) -> None:
        task = await self._task_repo.get_by_id(Id.from_string(command.task_id))
        if task is None:
            raise TaskNotFoundException(id=command.task_id)

        await self._permission_checker.require_permission(
            user_id=command.changed_by,
            project_id=str(task.project_id),
            permission=self.REQUIRED_PERMISSION,
        )

        if not await self._sprint_port.sprint_exists(command.sprint_id):
            raise TaskSprintNotAvailableException(command.sprint_id, "спринт не найден")

        sprint_data = await self._sprint_port.get_sprint(command.sprint_id)
        if sprint_data and sprint_data.get("status") not in ("PLANNING", "ACTIVE"):
            raise TaskSprintNotAvailableException(command.sprint_id, "спринт не в статусе PLANNING/ACTIVE")

        old_sprint = str(task.sprint_id) if task.sprint_id else None
        task.assign_to_sprint(Id.from_string(command.sprint_id))
        await self._task_repo.update(task)
        await self._event_bus.publish_all(task.clear_domain_events())

        entry = ChangelogEntry.create(
            task_id=Id.from_string(command.task_id),
            field_name="sprint_id",
            old_value=old_sprint,
            new_value=command.sprint_id,
            changed_by=Id.from_string(command.changed_by),
        )
        await self._changelog_repo.add(entry)

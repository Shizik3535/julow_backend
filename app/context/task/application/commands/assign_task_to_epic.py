from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.exceptions.task_app_exceptions import TaskEpicNotAvailableException
from app.context.task.application.ports.authorization.task_permission_checker_port import (
    TaskPermissionCheckerPort,
)
from app.context.task.application.ports.integration.inboard.epic_port import EpicPort
from app.context.task.domain.aggregates.changelog import ChangelogEntry
from app.context.task.domain.exceptions.task_exceptions import TaskNotFoundException
from app.context.task.domain.repositories.changelog_repository import ChangelogRepository
from app.context.task.domain.repositories.task_repository import TaskRepository


class AssignTaskToEpicCommand(BaseCommand):
    """
    Команда привязки задачи к эпику.

    Атрибуты:
        task_id: ID задачи.
        epic_id: ID эпика.
        changed_by: ID изменившего.
    """

    task_id: str
    epic_id: str
    changed_by: str


class AssignTaskToEpicHandler(BaseCommandHandler[AssignTaskToEpicCommand, None]):
    """
    Обработчик привязки задачи к эпику.

    Проверяет существование и доступность эпика через EpicPort.
    """

    REQUIRED_PERMISSION = "tasks.update"

    def __init__(
        self,
        task_repo: TaskRepository,
        changelog_repo: ChangelogRepository,
        epic_port: EpicPort,
        permission_checker: TaskPermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._task_repo = task_repo
        self._changelog_repo = changelog_repo
        self._epic_port = epic_port
        self._permission_checker = permission_checker
        self._event_bus = event_bus

    async def handle(self, command: AssignTaskToEpicCommand) -> None:
        task = await self._task_repo.get_by_id(Id.from_string(command.task_id))
        if task is None:
            raise TaskNotFoundException(id=command.task_id)

        await self._permission_checker.require_permission(
            user_id=command.changed_by,
            project_id=str(task.project_id),
            permission=self.REQUIRED_PERMISSION,
        )

        if not await self._epic_port.epic_exists(command.epic_id):
            raise TaskEpicNotAvailableException(command.epic_id, "эпик не найден")

        epic_data = await self._epic_port.get_epic(command.epic_id)
        if epic_data and epic_data.get("status") == "CANCELLED":
            raise TaskEpicNotAvailableException(command.epic_id, "эпик отменён")

        old_epic = str(task.epic_id) if task.epic_id else None
        task.assign_to_epic(Id.from_string(command.epic_id))
        await self._task_repo.update(task)
        await self._event_bus.publish_all(task.clear_domain_events())

        entry = ChangelogEntry.create(
            task_id=Id.from_string(command.task_id),
            field_name="epic_id",
            old_value=old_epic,
            new_value=command.epic_id,
            changed_by=Id.from_string(command.changed_by),
        )
        await self._changelog_repo.add(entry)

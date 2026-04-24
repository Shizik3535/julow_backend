from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.exceptions.task_app_exceptions import TaskStatusTransitionNotAllowedException
from app.context.task.application.ports.authorization.task_permission_checker_port import (
    TaskPermissionCheckerPort,
)
from app.context.task.application.ports.integration.inboard.board_port import BoardPort
from app.context.task.domain.aggregates.changelog import ChangelogEntry
from app.context.task.domain.exceptions.task_exceptions import TaskNotFoundException
from app.context.task.domain.repositories.changelog_repository import ChangelogRepository
from app.context.task.domain.repositories.task_repository import TaskRepository


class ChangeTaskStatusCommand(BaseCommand):
    """
    Команда смены workflow-статуса задачи.

    Атрибуты:
        task_id: ID задачи.
        new_status_id: ID нового workflow-статуса.
        changed_by: ID изменившего.
    """

    task_id: str
    new_status_id: str
    changed_by: str


class ChangeTaskStatusHandler(BaseCommandHandler[ChangeTaskStatusCommand, None]):
    """
    Обработчик смены workflow-статуса.

    Валидирует переход через BoardPort.is_transition_allowed.
    """

    REQUIRED_PERMISSION = "tasks.update"

    def __init__(
        self,
        task_repo: TaskRepository,
        changelog_repo: ChangelogRepository,
        board_port: BoardPort,
        permission_checker: TaskPermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._task_repo = task_repo
        self._changelog_repo = changelog_repo
        self._board_port = board_port
        self._permission_checker = permission_checker
        self._event_bus = event_bus

    async def handle(self, command: ChangeTaskStatusCommand) -> None:
        task = await self._task_repo.get_by_id(Id.from_string(command.task_id))
        if task is None:
            raise TaskNotFoundException(id=command.task_id)

        await self._permission_checker.require_permission(
            user_id=command.changed_by,
            project_id=str(task.project_id),
            permission=self.REQUIRED_PERMISSION,
        )

        old_status_id = str(task.status_id) if task.status_id else ""

        if task.status_id:
            allowed = await self._board_port.is_transition_allowed(
                project_id=str(task.project_id),
                from_status_id=old_status_id,
                to_status_id=command.new_status_id,
            )
            if not allowed:
                raise TaskStatusTransitionNotAllowedException(old_status_id, command.new_status_id)

        task.change_status(Id.from_string(command.new_status_id))
        await self._task_repo.update(task)
        await self._event_bus.publish_all(task.clear_domain_events())

        entry = ChangelogEntry.create(
            task_id=Id.from_string(command.task_id),
            field_name="status_id",
            old_value=old_status_id,
            new_value=command.new_status_id,
            changed_by=Id.from_string(command.changed_by),
        )
        await self._changelog_repo.add(entry)

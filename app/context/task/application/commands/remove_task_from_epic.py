from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.ports.authorization.task_permission_checker_port import (
    TaskPermissionCheckerPort,
)
from app.context.task.domain.aggregates.changelog import ChangelogEntry
from app.context.task.domain.exceptions.task_exceptions import TaskNotFoundException
from app.context.task.domain.repositories.changelog_repository import ChangelogRepository
from app.context.task.domain.repositories.task_repository import TaskRepository


class RemoveTaskFromEpicCommand(BaseCommand):
    """
    Команда убирания задачи из эпика.

    Атрибуты:
        caller_id: ID вызывающего.
        task_id: ID задачи.
        changed_by: ID изменившего.
    """

    caller_id: str
    task_id: str
    changed_by: str


class RemoveTaskFromEpicHandler(BaseCommandHandler[RemoveTaskFromEpicCommand, None]):
    """Обработчик убирания задачи из эпика."""

    REQUIRED_PERMISSION = "tasks.update"

    def __init__(
        self,
        task_repo: TaskRepository,
        changelog_repo: ChangelogRepository,
        permission_checker: TaskPermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._task_repo = task_repo
        self._changelog_repo = changelog_repo
        self._permission_checker = permission_checker
        self._event_bus = event_bus

    async def handle(self, command: RemoveTaskFromEpicCommand) -> None:
        task = await self._task_repo.get_by_id(Id.from_string(command.task_id))
        if task is None:
            raise TaskNotFoundException(id=command.task_id)

        await self._permission_checker.require_permission(
            user_id=command.caller_id,
            project_id=str(task.project_id),
            permission=self.REQUIRED_PERMISSION,
        )

        old_epic = str(task.epic_id) if task.epic_id else None
        task.remove_from_epic()
        await self._task_repo.update(task)
        await self._event_bus.publish_all(task.clear_domain_events())

        entry = ChangelogEntry.create(
            task_id=Id.from_string(command.task_id),
            field_name="epic_id",
            old_value=old_epic,
            new_value=None,
            changed_by=Id.from_string(command.changed_by),
        )
        await self._changelog_repo.add(entry)

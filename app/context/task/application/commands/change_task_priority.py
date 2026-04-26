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
from app.context.task.domain.value_objects.task_priority import TaskPriority


class ChangeTaskPriorityCommand(BaseCommand):
    """
    Команда смены приоритета задачи.

    Атрибуты:
        task_id: ID задачи.
        new_priority: Новый приоритет.
        changed_by: ID изменившего.
    """

    task_id: str
    new_priority: str
    changed_by: str


class ChangeTaskPriorityHandler(BaseCommandHandler[ChangeTaskPriorityCommand, None]):
    """Обработчик смены приоритета задачи."""

    REQUIRED_PERMISSION = "tasks.update_own"

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

    async def handle(self, command: ChangeTaskPriorityCommand) -> None:
        task = await self._task_repo.get_by_id(Id.from_string(command.task_id))
        if task is None:
            raise TaskNotFoundException(id=command.task_id)

        await self._permission_checker.require_permission(
            user_id=command.changed_by,
            project_id=str(task.project_id),
            permission=self.REQUIRED_PERMISSION,
        )

        old_priority = task.priority.value
        task.change_priority(TaskPriority(command.new_priority))
        await self._task_repo.update(task)
        await self._event_bus.publish_all(task.clear_domain_events())

        entry = ChangelogEntry.create(
            task_id=Id.from_string(command.task_id),
            field_name="priority",
            old_value=old_priority,
            new_value=command.new_priority,
            changed_by=Id.from_string(command.changed_by),
        )
        await self._changelog_repo.add(entry)

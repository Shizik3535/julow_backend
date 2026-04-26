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


class RemoveTaskCustomFieldCommand(BaseCommand):
    """
    Команда удаления кастомного поля задачи.

    Атрибуты:
        task_id: ID задачи.
        field_name: Имя поля.
        changed_by: ID изменившего.
    """

    caller_id: str
    task_id: str
    field_name: str
    changed_by: str


class RemoveTaskCustomFieldHandler(BaseCommandHandler[RemoveTaskCustomFieldCommand, None]):
    """Обработчик удаления кастомного поля задачи."""

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

    async def handle(self, command: RemoveTaskCustomFieldCommand) -> None:
        task = await self._task_repo.get_by_id(Id.from_string(command.task_id))
        if task is None:
            raise TaskNotFoundException(id=command.task_id)

        await self._permission_checker.require_permission(
            user_id=command.caller_id,
            project_id=str(task.project_id),
            permission=self.REQUIRED_PERMISSION,
        )

        old_value = task.custom_fields.get(command.field_name)
        task.remove_custom_field(command.field_name)
        await self._task_repo.update(task)
        await self._event_bus.publish_all(task.clear_domain_events())

        if old_value is not None:
            entry = ChangelogEntry.create(
                task_id=Id.from_string(command.task_id),
                field_name=f"custom_field:{command.field_name}",
                old_value=old_value,
                new_value=None,
                changed_by=Id.from_string(command.changed_by),
            )
            await self._changelog_repo.add(entry)

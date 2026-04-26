from __future__ import annotations

from datetime import date

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
from app.context.task.domain.value_objects.recurrence_config import RecurrenceConfig
from app.context.task.domain.value_objects.recurrence_pattern import RecurrencePattern


class SetTaskRecurrenceCommand(BaseCommand):
    """
    Команда установки конфигурации повторения задачи.

    Атрибуты:
        caller_id: ID вызывающего.
        task_id: ID задачи.
        pattern: Паттерн повторения.
        interval: Интервал.
        end_date: Дата окончания (ISO).
        max_occurrences: Максимум повторений.
        changed_by: ID изменившего.
    """

    caller_id: str
    task_id: str
    pattern: str
    interval: int = 1
    end_date: str | None = None
    max_occurrences: int | None = None
    changed_by: str


class SetTaskRecurrenceHandler(BaseCommandHandler[SetTaskRecurrenceCommand, None]):
    """Обработчик установки конфигурации повторения задачи."""

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

    async def handle(self, command: SetTaskRecurrenceCommand) -> None:
        task = await self._task_repo.get_by_id(Id.from_string(command.task_id))
        if task is None:
            raise TaskNotFoundException(id=command.task_id)

        await self._permission_checker.require_permission(
            user_id=command.caller_id,
            project_id=str(task.project_id),
            permission=self.REQUIRED_PERMISSION,
        )

        old_pattern = task.recurrence.pattern.value if task.recurrence else None
        config = RecurrenceConfig(
            pattern=RecurrencePattern(command.pattern),
            interval=command.interval,
            end_date=date.fromisoformat(command.end_date) if command.end_date else None,
            max_occurrences=command.max_occurrences,
        )
        task.set_recurrence(config)
        await self._task_repo.update(task)
        await self._event_bus.publish_all(task.clear_domain_events())

        entry = ChangelogEntry.create(
            task_id=Id.from_string(command.task_id),
            field_name="recurrence_pattern",
            old_value=old_pattern,
            new_value=command.pattern,
            changed_by=Id.from_string(command.changed_by),
        )
        await self._changelog_repo.add(entry)

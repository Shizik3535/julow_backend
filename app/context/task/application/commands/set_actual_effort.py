from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.task.domain.aggregates.changelog import ChangelogEntry
from app.context.task.domain.exceptions.task_exceptions import TaskNotFoundException
from app.context.task.domain.repositories.changelog_repository import ChangelogRepository
from app.context.task.domain.repositories.task_repository import TaskRepository
from app.context.task.domain.value_objects.actual_effort import ActualEffort
from app.context.task.domain.value_objects.effort_unit import EffortUnit


class SetActualEffortCommand(BaseCommand):
    """
    Команда установки фактического усилия.

    Атрибуты:
        task_id: ID задачи.
        value: Значение.
        unit: Единица.
        changed_by: ID изменившего.
    """

    task_id: str
    value: float
    unit: str
    changed_by: str


class SetActualEffortHandler(BaseCommandHandler[SetActualEffortCommand, None]):
    """Обработчик установки фактического усилия."""

    def __init__(
        self,
        task_repo: TaskRepository,
        changelog_repo: ChangelogRepository,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._task_repo = task_repo
        self._changelog_repo = changelog_repo
        self._event_bus = event_bus

    async def handle(self, command: SetActualEffortCommand) -> None:
        task = await self._task_repo.get_by_id(Id.from_string(command.task_id))
        if task is None:
            raise TaskNotFoundException(id=command.task_id)

        old_value = f"{task.actual_effort.value} {task.actual_effort.unit.value}" if task.actual_effort else None
        effort = ActualEffort(value=command.value, unit=EffortUnit(command.unit))
        task.set_actual_effort(effort)
        await self._task_repo.update(task)
        await self._event_bus.publish_all(task.clear_domain_events())

        entry = ChangelogEntry.create(
            task_id=Id.from_string(command.task_id),
            field_name="actual_effort",
            old_value=old_value,
            new_value=f"{command.value} {command.unit}",
            changed_by=Id.from_string(command.changed_by),
        )
        await self._changelog_repo.add(entry)

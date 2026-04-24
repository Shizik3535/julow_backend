from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.task.domain.aggregates.changelog import ChangelogEntry
from app.context.task.domain.exceptions.task_exceptions import TaskNotFoundException
from app.context.task.domain.repositories.changelog_repository import ChangelogRepository
from app.context.task.domain.repositories.task_repository import TaskRepository


class RemoveTaskFromSprintCommand(BaseCommand):
    """
    Команда убирания задачи из спринта.

    Атрибуты:
        task_id: ID задачи.
        changed_by: ID изменившего.
    """

    task_id: str
    changed_by: str


class RemoveTaskFromSprintHandler(BaseCommandHandler[RemoveTaskFromSprintCommand, None]):
    """Обработчик убирания задачи из спринта."""

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

    async def handle(self, command: RemoveTaskFromSprintCommand) -> None:
        task = await self._task_repo.get_by_id(Id.from_string(command.task_id))
        if task is None:
            raise TaskNotFoundException(id=command.task_id)

        old_sprint = str(task.sprint_id) if task.sprint_id else None
        task.remove_from_sprint()
        await self._task_repo.update(task)
        await self._event_bus.publish_all(task.clear_domain_events())

        entry = ChangelogEntry.create(
            task_id=Id.from_string(command.task_id),
            field_name="sprint_id",
            old_value=old_sprint,
            new_value=None,
            changed_by=Id.from_string(command.changed_by),
        )
        await self._changelog_repo.add(entry)

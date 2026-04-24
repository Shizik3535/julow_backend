from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.task.domain.exceptions.task_exceptions import TaskNotFoundException
from app.context.task.domain.repositories.task_repository import TaskRepository


class ToggleChecklistItemCommand(BaseCommand):
    """
    Команда отметки/снятия пункта чек-листа.

    Атрибуты:
        task_id: ID задачи.
        checklist_id: ID чек-листа.
        item_id: ID пункта.
    """

    task_id: str
    checklist_id: str
    item_id: str


class ToggleChecklistItemHandler(BaseCommandHandler[ToggleChecklistItemCommand, None]):
    """Обработчик отметки/снятия пункта чек-листа."""

    def __init__(self, task_repo: TaskRepository, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._task_repo = task_repo
        self._event_bus = event_bus

    async def handle(self, command: ToggleChecklistItemCommand) -> None:
        task = await self._task_repo.get_by_id(Id.from_string(command.task_id))
        if task is None:
            raise TaskNotFoundException(id=command.task_id)

        task.toggle_checklist_item(
            checklist_id=Id.from_string(command.checklist_id),
            item_id=Id.from_string(command.item_id),
        )
        await self._task_repo.update(task)
        await self._event_bus.publish_all(task.clear_domain_events())

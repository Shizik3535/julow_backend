from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.task.domain.exceptions.task_exceptions import TaskNotFoundException
from app.context.task.domain.repositories.task_repository import TaskRepository


class RemoveChecklistCommand(BaseCommand):
    """
    Команда удаления чек-листа.

    Атрибуты:
        task_id: ID задачи.
        checklist_id: ID чек-листа.
    """

    task_id: str
    checklist_id: str


class RemoveChecklistHandler(BaseCommandHandler[RemoveChecklistCommand, None]):
    """Обработчик удаления чек-листа."""

    def __init__(self, task_repo: TaskRepository, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._task_repo = task_repo
        self._event_bus = event_bus

    async def handle(self, command: RemoveChecklistCommand) -> None:
        task = await self._task_repo.get_by_id(Id.from_string(command.task_id))
        if task is None:
            raise TaskNotFoundException(id=command.task_id)

        task.remove_checklist(Id.from_string(command.checklist_id))
        await self._task_repo.update(task)
        await self._event_bus.publish_all(task.clear_domain_events())

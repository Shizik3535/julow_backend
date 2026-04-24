from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.task.domain.exceptions.task_exceptions import TaskNotFoundException
from app.context.task.domain.repositories.task_repository import TaskRepository


class AddChecklistCommand(BaseCommand):
    """
    Команда добавления чек-листа.

    Атрибуты:
        task_id: ID задачи.
        title: Заголовок чек-листа.
    """

    task_id: str
    title: str


class AddChecklistHandler(BaseCommandHandler[AddChecklistCommand, str]):
    """Обработчик добавления чек-листа. Возвращает ID чек-листа."""

    def __init__(self, task_repo: TaskRepository, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._task_repo = task_repo
        self._event_bus = event_bus

    async def handle(self, command: AddChecklistCommand) -> str:
        task = await self._task_repo.get_by_id(Id.from_string(command.task_id))
        if task is None:
            raise TaskNotFoundException(id=command.task_id)

        checklist = task.add_checklist(command.title)
        await self._task_repo.update(task)
        await self._event_bus.publish_all(task.clear_domain_events())
        return str(checklist.id)

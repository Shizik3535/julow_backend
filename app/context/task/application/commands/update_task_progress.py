from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.task.domain.exceptions.task_exceptions import TaskNotFoundException
from app.context.task.domain.repositories.task_repository import TaskRepository
from app.context.task.domain.value_objects.task_progress import TaskProgress


class UpdateTaskProgressCommand(BaseCommand):
    """
    Команда обновления прогресса задачи.

    Атрибуты:
        task_id: ID задачи.
        progress: Прогресс (0–100).
    """

    task_id: str
    progress: int


class UpdateTaskProgressHandler(BaseCommandHandler[UpdateTaskProgressCommand, None]):
    """Обработчик обновления прогресса задачи."""

    def __init__(self, task_repo: TaskRepository, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._task_repo = task_repo
        self._event_bus = event_bus

    async def handle(self, command: UpdateTaskProgressCommand) -> None:
        task = await self._task_repo.get_by_id(Id.from_string(command.task_id))
        if task is None:
            raise TaskNotFoundException(id=command.task_id)

        task.update_progress(TaskProgress(value=command.progress))
        await self._task_repo.update(task)
        await self._event_bus.publish_all(task.clear_domain_events())

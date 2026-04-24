from __future__ import annotations

from app.shared.application.base_event_handler import BaseEventHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.task.domain.aggregates.task import Task
from app.context.task.domain.events.task_events import TaskStatusChanged, RecurringTaskCreated
from app.context.task.domain.repositories.task_repository import TaskRepository


class OnTaskCompletedCreateRecurring(BaseEventHandler[TaskStatusChanged]):
    """
    Обработчик события TaskStatusChanged (intra-BC).

    Если задача имеет recurrence и статус сменился на «done»,
    автоматически создаёт следующую задачу.
    """

    def __init__(
        self,
        task_repo: TaskRepository,
        event_bus: DomainEventBus,
        done_status_ids: list[str] | None = None,
    ) -> None:
        super().__init__()
        self._task_repo = task_repo
        self._event_bus = event_bus
        self._done_status_ids = done_status_ids or []

    async def handle(self, event: TaskStatusChanged) -> None:
        if event.new_status_id not in self._done_status_ids:
            return

        task = await self._task_repo.get_by_id(Id.from_string(event.task_id))
        if task is None or task.recurrence is None:
            return

        new_task = Task.create(
            title=task.title,
            project_id=task.project_id,
            task_type=task.task_type,
            reporter_id=task.reporter_id or Id.generate(),
            parent_task_id=task.parent_task_id,
            epic_id=task.epic_id,
        )
        new_task.set_recurrence(task.recurrence)

        if task.sprint_id:
            new_task.assign_to_sprint(task.sprint_id)

        await self._task_repo.add(new_task)

        events = new_task.clear_domain_events()
        events.append(
            RecurringTaskCreated(
                source_task_id=str(task.id),
                new_task_id=str(new_task.id),
            )
        )
        await self._event_bus.publish_all(events)

        self._logger.info(
            "Created recurring task",
            source_task_id=event.task_id,
            new_task_id=str(new_task.id),
        )

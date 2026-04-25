from __future__ import annotations

from typing import Any

from app.shared.application.base_event_handler import BaseEventHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.task.domain.repositories.task_repository import TaskRepository


class OnSprintCompleted(BaseEventHandler[dict[str, Any]]):
    """
    Обработчик события SprintCompleted из Project BC.

    Убирает sprint_id у задач завершённого спринта.
    Если есть next_sprint_id — переносит задачи в следующий спринт.
    Подписывается на топик «project.events».
    """

    def __init__(self, task_repo: TaskRepository, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._task_repo = task_repo
        self._event_bus = event_bus

    async def handle(self, event: dict[str, Any]) -> None:
        event_type = event.get("event_type")
        if event_type != "SprintCompleted":
            return

        payload = event.get("payload", {})
        sprint_id_str = payload.get("sprint_id")
        if not sprint_id_str:
            self._logger.warning("SprintCompleted missing sprint_id", raw_event=event)
            return

        next_sprint_id_str = payload.get("next_sprint_id")
        tasks = await self._task_repo.get_by_sprint(Id.from_string(sprint_id_str))

        for task in tasks:
            if next_sprint_id_str:
                task.remove_from_sprint()
                task.assign_to_sprint(Id.from_string(next_sprint_id_str))
            else:
                task.remove_from_sprint()
            await self._task_repo.update(task)
            await self._event_bus.publish_all(task.clear_domain_events())

        self._logger.info(
            "Processed sprint completed",
            sprint_id=sprint_id_str,
            next_sprint_id=next_sprint_id_str,
            count=len(tasks),
        )

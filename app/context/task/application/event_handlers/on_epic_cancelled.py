from __future__ import annotations

from typing import Any

from app.shared.application.base_event_handler import BaseEventHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.task.domain.repositories.task_repository import TaskRepository


class OnEpicCancelled(BaseEventHandler[dict[str, Any]]):
    """
    Обработчик события EpicStatusChanged(CANCELLED) из Project BC.

    Убирает epic_id у задач, привязанных к отменённому эпику.
    Подписывается на топик «project.events».
    """

    def __init__(self, task_repo: TaskRepository, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._task_repo = task_repo
        self._event_bus = event_bus

    async def handle(self, event: dict[str, Any]) -> None:
        event_type = event.get("event_type")
        if event_type != "EpicStatusChanged":
            return

        payload = event.get("payload", {})
        new_status = payload.get("new_status")
        if new_status != "CANCELLED":
            return

        epic_id_str = payload.get("epic_id")
        if not epic_id_str:
            self._logger.warning("EpicStatusChanged missing epic_id", raw_event=event)
            return

        tasks = await self._task_repo.get_by_epic(Id.from_string(epic_id_str))
        for task in tasks:
            task.remove_from_epic()
            await self._task_repo.update(task)
            await self._event_bus.publish_all(task.clear_domain_events())

        self._logger.info(
            "Removed tasks from cancelled epic",
            epic_id=epic_id_str,
            count=len(tasks),
        )

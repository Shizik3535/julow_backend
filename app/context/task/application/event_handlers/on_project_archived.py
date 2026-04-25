from __future__ import annotations

from typing import Any

from app.shared.application.base_event_handler import BaseEventHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.task.domain.repositories.task_repository import TaskRepository


class OnProjectArchived(BaseEventHandler[dict[str, Any]]):
    """
    Обработчик события ProjectArchived из Project BC.

    Архивирует все задачи проекта.
    Подписывается на топик «project.events».
    """

    def __init__(self, task_repo: TaskRepository, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._task_repo = task_repo
        self._event_bus = event_bus

    async def handle(self, event: dict[str, Any]) -> None:
        event_type = event.get("event_type")
        if event_type != "ProjectArchived":
            return

        payload = event.get("payload", {})
        project_id_str = payload.get("project_id")
        if not project_id_str:
            self._logger.warning("ProjectArchived missing project_id", raw_event=event)
            return

        tasks = await self._task_repo.get_by_project(Id.from_string(project_id_str))
        for task in tasks:
            task.archive()
            await self._task_repo.update(task)
            await self._event_bus.publish_all(task.clear_domain_events())

        self._logger.info(
            "Archived tasks for project",
            project_id=project_id_str,
            count=len(tasks),
        )

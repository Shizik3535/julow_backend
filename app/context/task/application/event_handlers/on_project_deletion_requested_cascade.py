from __future__ import annotations

from typing import Any

from app.shared.application.base_event_handler import BaseEventHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.task.domain.repositories.task_repository import TaskRepository
from app.context.task.domain.value_objects.task_status import TaskStatus


class OnProjectDeletionRequestedCascade(BaseEventHandler[dict[str, Any]]):
    """
    Обработчик события ProjectDeletionRequested из Project BC.

    Мягко удаляет все задачи проекта.
    Подписывается на топик «project.events».
    """

    def __init__(
        self,
        task_repo: TaskRepository,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._task_repo = task_repo
        self._event_bus = event_bus

    async def handle(self, event: dict[str, Any]) -> None:
        event_type = event.get("event_type")
        if event_type != "ProjectDeletionRequested":
            return

        payload = event.get("payload", {})
        project_id_str = payload.get("project_id")
        if not project_id_str:
            self._logger.warning(
                "ProjectDeletionRequested missing project_id",
                raw_event=event,
            )
            return

        project_id = Id.from_string(project_id_str)
        tasks = await self._task_repo.get_by_project(project_id)
        
        deleted_count = 0
        for task in tasks:
            if task.status == TaskStatus.DELETED:
                continue  # Уже удалена

            task.soft_delete()
            await self._task_repo.update(task)
            await self._event_bus.publish_all(task.clear_domain_events())
            deleted_count += 1

        self._logger.info(
            "Soft deleted tasks for project",
            project_id=str(project_id),
            count=deleted_count,
        )

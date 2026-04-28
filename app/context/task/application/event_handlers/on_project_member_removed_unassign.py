from __future__ import annotations

from typing import Any

from app.shared.application.base_event_handler import BaseEventHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.task.domain.repositories.task_repository import TaskRepository


class OnProjectMemberRemovedUnassign(BaseEventHandler[dict[str, Any]]):
    """
    Обработчик события ProjectMemberRemoved из Project BC.

    Снимает назначение пользователя со всех задач проекта.
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
        if event_type != "ProjectMemberRemoved":
            return

        payload = event.get("payload", {})
        project_id_str = payload.get("project_id")
        user_id_str = payload.get("user_id")
        
        if not project_id_str or not user_id_str:
            self._logger.warning(
                "ProjectMemberRemoved missing project_id or user_id",
                raw_event=event,
            )
            return

        project_id = Id.from_string(project_id_str)
        user_id = Id.from_string(user_id_str)

        # Получаем все задачи, назначенные на пользователя в этом проекте
        tasks = await self._task_repo.get_by_assignee_in_project(user_id, project_id)
        
        unassigned_count = 0
        for task in tasks:
            if user_id not in task.assignee_ids:
                continue  # Уже не назначен

            task.unassign(user_id)
            await self._task_repo.update(task)
            await self._event_bus.publish_all(task.clear_domain_events())
            unassigned_count += 1

        self._logger.info(
            "Unassigned user from project tasks",
            user_id=str(user_id),
            project_id=str(project_id),
            count=unassigned_count,
        )

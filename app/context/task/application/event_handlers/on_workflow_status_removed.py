from __future__ import annotations

from typing import Any

from app.shared.application.base_event_handler import BaseEventHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.ports.integration.inboard.board_port import BoardPort
from app.context.task.domain.repositories.task_repository import TaskRepository


class OnWorkflowStatusRemoved(BaseEventHandler[dict[str, Any]]):
    """
    Обработчик события WorkflowStatusRemoved из Project BC.

    Сбрасывает status_id у задач с удалённым статусом на default.
    Подписывается на топик «project.events».
    """

    def __init__(
        self,
        task_repo: TaskRepository,
        board_port: BoardPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._task_repo = task_repo
        self._board_port = board_port
        self._event_bus = event_bus

    async def handle(self, event: dict[str, Any]) -> None:
        event_type = event.get("event_type")
        if event_type != "WorkflowStatusRemoved":
            return

        payload = event.get("payload", {})
        status_id_str = payload.get("status_id")
        project_id_str = payload.get("project_id")
        if not status_id_str or not project_id_str:
            self._logger.warning("WorkflowStatusRemoved missing fields", event=event)
            return

        default_status_id = await self._board_port.get_default_status_id(project_id_str)
        tasks = await self._task_repo.get_by_status(
            project_id=Id.from_string(project_id_str),
            status_id=Id.from_string(status_id_str),
        )

        for task in tasks:
            if default_status_id:
                task.change_status(Id.from_string(default_status_id))
            else:
                task.status_id = None
                from datetime import datetime, timezone
                task.updated_at = datetime.now(tz=timezone.utc)
            await self._task_repo.update(task)
            await self._event_bus.publish_all(task.clear_domain_events())

        self._logger.info(
            "Reset tasks from removed workflow status",
            project_id=project_id_str,
            removed_status=status_id_str,
            default_status=default_status_id,
            count=len(tasks),
        )

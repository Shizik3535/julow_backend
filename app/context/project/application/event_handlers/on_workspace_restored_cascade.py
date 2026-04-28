from __future__ import annotations

from typing import Any

from app.shared.application.base_event_handler import BaseEventHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.domain.repositories.project_repository import ProjectRepository
from app.context.project.domain.value_objects.project_status import ProjectStatus


class OnWorkspaceRestoredCascade(BaseEventHandler[dict[str, Any]]):
    """
    Обработчик события WorkspaceRestored из Workspace BC.

    Восстанавливает все архивированные проекты workspace.
    Подписывается на топик «workspace.events».
    """

    def __init__(
        self,
        project_repo: ProjectRepository,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._project_repo = project_repo
        self._event_bus = event_bus

    async def handle(self, event: dict[str, Any]) -> None:
        event_type = event.get("event_type")
        if event_type != "WorkspaceRestored":
            return

        payload = event.get("payload", {})
        workspace_id_str = payload.get("workspace_id")
        if not workspace_id_str:
            self._logger.warning(
                "WorkspaceRestored missing workspace_id",
                raw_event=event,
            )
            return

        workspace_id = Id.from_string(workspace_id_str)
        projects = await self._project_repo.get_by_workspace(workspace_id)
        
        restored_count = 0
        for project in projects:
            if project.status != ProjectStatus.ARCHIVED:
                continue  # Не архивирован, пропускаем

            project.restore()
            await self._project_repo.update(project)
            await self._event_bus.publish_all(project.clear_domain_events())
            restored_count += 1

        self._logger.info(
            "Restored projects for workspace",
            workspace_id=str(workspace_id),
            count=restored_count,
        )

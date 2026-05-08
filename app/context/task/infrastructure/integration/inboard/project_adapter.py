from __future__ import annotations

from typing import Any

from app.context.project.application.ports.integration.outboard.project_provider import (
    ProjectProvider,
)
from app.context.task.application.ports.integration.inboard.project_port import (
    ProjectPort,
)


class ProjectAdapter(ProjectPort):
    """
    Реализация inboard-порта ProjectPort для Task BC.

    Делегирует получение данных проекта в outboard-порт
    Project BC (ProjectProvider).
    """

    def __init__(self, project_provider: ProjectProvider) -> None:
        self._provider = project_provider

    async def project_exists(self, project_id: str) -> bool:
        return await self._provider.project_exists(project_id)

    async def get_project(self, project_id: str) -> dict[str, Any] | None:
        dto = await self._provider.get_project(project_id)
        if dto is None:
            return None
        return {
            "id": dto.id,
            "name": dto.name,
            "status": getattr(dto, "status", None),
            "workspace_id": getattr(dto, "workspace_id", None),
        }

    async def is_project_active(self, project_id: str) -> bool:
        dto = await self._provider.get_project(project_id)
        if dto is None:
            return False
        status = getattr(dto, "status", None)
        return status is not None and status.lower() not in ("archived", "suspended")

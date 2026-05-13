from __future__ import annotations

from app.context.project.application.ports.integration.outboard.project_provider import (
    ProjectProvider,
)
from app.context.timetracking.application.ports.integration.inboard.project_port import (
    ProjectPort,
)


class ProjectAdapter(ProjectPort):
    """Inboard ProjectPort для TimeTracking BC. Делегирует в outboard Project BC."""

    def __init__(self, project_provider: ProjectProvider) -> None:
        self._provider = project_provider

    async def project_exists(self, project_id: str) -> bool:
        return await self._provider.project_exists(project_id)

    async def is_project_active(self, project_id: str) -> bool:
        dto = await self._provider.get_project(project_id)
        if dto is None:
            return False
        status = getattr(dto, "status", None)
        return status is not None and str(status).lower() not in ("archived", "suspended")

    async def get_project_workspace_id(self, project_id: str) -> str | None:
        dto = await self._provider.get_project(project_id)
        if dto is None:
            return None
        return getattr(dto, "workspace_id", None)

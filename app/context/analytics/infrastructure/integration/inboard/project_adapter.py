from __future__ import annotations

from app.context.analytics.application.ports.integration.inboard.project_port import (
    ProjectPort,
)
from app.context.project.application.ports.integration.outboard.project_provider import (
    ProjectProvider,
)


class ProjectAdapter(ProjectPort):
    """Inboard ``ProjectPort`` для Analytics BC. Делегирует в outboard Project BC."""

    def __init__(self, project_provider: ProjectProvider) -> None:
        self._provider = project_provider

    async def project_exists(self, project_id: str) -> bool:
        return await self._provider.project_exists(project_id=project_id)

    async def project_workspace_id(self, project_id: str) -> str | None:
        dto = await self._provider.get_project(project_id=project_id)
        if dto is None:
            return None
        return str(dto.workspace_id) if dto.workspace_id is not None else None

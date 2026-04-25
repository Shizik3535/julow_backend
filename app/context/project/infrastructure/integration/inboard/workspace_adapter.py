from __future__ import annotations

from app.context.project.application.ports.integration.inboard.workspace_port import (
    WorkspacePort,
)
from app.context.workspace.application.ports.integration.outboard.workspace_provider import (
    WorkspaceProvider,
)


class WorkspaceAdapter(WorkspacePort):
    """
    Реализация WorkspacePort для Project BC.

    Делегирует в WorkspaceProvider (outboard Workspace BC).
    """

    def __init__(self, workspace_provider: WorkspaceProvider) -> None:
        self._provider = workspace_provider

    async def workspace_exists(self, workspace_id: str) -> bool:
        return await self._provider.workspace_exists(workspace_id=workspace_id)

    async def get_workspace(self, workspace_id: str) -> dict | None:
        ws = await self._provider.get_workspace(workspace_id=workspace_id)
        if ws is None:
            return None
        return {
            "id": ws.id,
            "name": ws.name,
            "organization_id": ws.organization_id,
        }

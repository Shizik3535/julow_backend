from __future__ import annotations

from typing import Any

from app.context.filestorage.application.ports.integration.inboard.workspace_port import (
    WorkspacePort,
)
from app.context.workspace.application.ports.integration.outboard.workspace_provider import (
    WorkspaceProvider,
)


class WorkspaceAdapter(WorkspacePort):
    """Реализация WorkspacePort для FileStorage BC через Workspace outboard."""

    def __init__(self, workspace_provider: WorkspaceProvider) -> None:
        self._provider = workspace_provider

    async def workspace_exists(self, workspace_id: str) -> bool:
        ws = await self._provider.get_workspace(workspace_id=workspace_id)
        return ws is not None

    async def get_workspace(self, workspace_id: str) -> dict[str, Any] | None:
        ws = await self._provider.get_workspace(workspace_id=workspace_id)
        if ws is None:
            return None
        return {"id": str(ws.id), "name": getattr(ws, "name", "")}

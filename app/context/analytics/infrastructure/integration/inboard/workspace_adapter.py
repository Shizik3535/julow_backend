from __future__ import annotations

from app.context.analytics.application.ports.integration.inboard.workspace_port import (
    WorkspacePort,
)
from app.context.workspace.application.ports.integration.outboard.workspace_membership_provider import (
    WorkspaceMembershipProvider,
)
from app.context.workspace.application.ports.integration.outboard.workspace_provider import (
    WorkspaceProvider,
)


class WorkspaceAdapter(WorkspacePort):
    """Inboard ``WorkspacePort`` для Analytics BC. Делегирует в outboard Workspace BC."""

    def __init__(
        self,
        workspace_provider: WorkspaceProvider,
        workspace_membership_provider: WorkspaceMembershipProvider,
    ) -> None:
        self._provider = workspace_provider
        self._membership = workspace_membership_provider

    async def workspace_exists(self, workspace_id: str) -> bool:
        return await self._provider.workspace_exists(workspace_id=workspace_id)

    async def is_member(self, workspace_id: str, user_id: str) -> bool:
        return await self._membership.is_member(
            workspace_id=workspace_id, user_id=user_id
        )

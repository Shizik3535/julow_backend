from __future__ import annotations

from app.context.timetracking.application.ports.integration.inboard.workspace_port import (
    WorkspacePort,
)
from app.context.workspace.application.ports.integration.outboard.workspace_membership_provider import (
    WorkspaceMembershipProvider,
)
from app.context.workspace.application.ports.integration.outboard.workspace_provider import (
    WorkspaceProvider,
)


class WorkspaceAdapter(WorkspacePort):
    """Inboard WorkspacePort для TimeTracking BC.

    Делегирует в outboard WorkspaceProvider / WorkspaceMembershipProvider
    из Workspace BC.
    """

    def __init__(
        self,
        workspace_provider: WorkspaceProvider,
        workspace_membership_provider: WorkspaceMembershipProvider,
    ) -> None:
        self._workspace_provider = workspace_provider
        self._membership_provider = workspace_membership_provider

    async def workspace_exists(self, workspace_id: str) -> bool:
        return await self._workspace_provider.workspace_exists(workspace_id)

    async def is_member(self, workspace_id: str, user_id: str) -> bool:
        return await self._membership_provider.is_member(
            workspace_id=workspace_id, user_id=user_id
        )

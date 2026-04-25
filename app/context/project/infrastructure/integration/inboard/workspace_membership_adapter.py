from __future__ import annotations

from app.context.project.application.ports.integration.inboard.workspace_membership_port import (
    WorkspaceMembershipPort,
)
from app.context.workspace.application.ports.integration.outboard.workspace_membership_provider import (
    WorkspaceMembershipProvider,
)


class WorkspaceMembershipAdapter(WorkspaceMembershipPort):
    """
    Реализация WorkspaceMembershipPort для Project BC.

    Делегирует в WorkspaceMembershipProvider (outboard Workspace BC).
    """

    def __init__(self, workspace_membership_provider: WorkspaceMembershipProvider) -> None:
        self._provider = workspace_membership_provider

    async def is_workspace_member(self, workspace_id: str, user_id: str) -> bool:
        return await self._provider.is_member(workspace_id=workspace_id, user_id=user_id)

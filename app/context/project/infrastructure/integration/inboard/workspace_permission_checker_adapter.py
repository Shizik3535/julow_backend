from __future__ import annotations

from app.context.project.application.ports.integration.inboard.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.workspace.application.ports.integration.outboard.workspace_membership_provider import (
    WorkspaceMembershipProvider,
)


class WorkspacePermissionCheckerAdapter(WorkspacePermissionCheckerPort):
    """
    Реализация WorkspacePermissionCheckerPort для Project BC.

    Делегирует в WorkspaceMembershipProvider (outboard Workspace BC),
    который инкапсулирует каскад workspace-роль → орг-роль.
    """

    def __init__(self, workspace_membership_provider: WorkspaceMembershipProvider) -> None:
        self._provider = workspace_membership_provider

    async def has_permission(self, user_id: str, workspace_id: str, permission: str) -> bool:
        return await self._provider.has_permission(
            workspace_id=workspace_id,
            user_id=user_id,
            permission=permission,
        )

    async def require_permission(self, user_id: str, workspace_id: str, permission: str) -> None:
        has = await self.has_permission(user_id=user_id, workspace_id=workspace_id, permission=permission)
        if not has:
            from app.context.project.application.exceptions.authorization_exceptions import (
                InsufficientProjectPermissionsException,
            )
            raise InsufficientProjectPermissionsException(
                permission=permission, project_id=workspace_id,
            )

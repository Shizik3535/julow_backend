from __future__ import annotations

from app.context.timetracking.application.exceptions.authorization_exceptions import (
    InsufficientTimeTrackingPermissionsException,
)
from app.context.timetracking.application.ports.authorization.timetracking_permission_checker_port import (
    TimeTrackingPermissionCheckerPort,
)
from app.context.workspace.application.ports.integration.outboard.workspace_membership_provider import (
    WorkspaceMembershipProvider,
)


class TimeTrackingRoleBasedPermissionChecker(TimeTrackingPermissionCheckerPort):
    """
    Проверка разрешений TimeTracking BC через каскад workspace-роль → орг-роль.

    Делегирует в WorkspaceMembershipProvider.has_permission (outboard
    Workspace BC), который инкапсулирует каскад workspace → org.
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
        if not await self.has_permission(
            user_id=user_id, workspace_id=workspace_id, permission=permission
        ):
            raise InsufficientTimeTrackingPermissionsException(
                permission=permission, workspace_id=workspace_id, user_id=user_id
            )

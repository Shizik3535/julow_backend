from __future__ import annotations

from app.context.analytics.application.exceptions.authorization_exceptions import (
    InsufficientAnalyticsPermissionsException,
)
from app.context.analytics.application.ports.authorization.analytics_permission_checker_port import (
    AnalyticsPermissionCheckerPort,
)
from app.context.workspace.application.ports.integration.outboard.workspace_membership_provider import (
    WorkspaceMembershipProvider,
)


class AnalyticsRoleBasedPermissionChecker(AnalyticsPermissionCheckerPort):
    """
    Реализация ``AnalyticsPermissionCheckerPort`` через каскад
    workspace-роль → орг-роль.

    Делегирует в ``WorkspaceMembershipProvider.has_permission`` (outboard
    Workspace BC), который инкапсулирует каскад workspace → org.
    Analytics BC не содержит собственного агрегата ролей.
    """

    def __init__(self, workspace_membership_provider: WorkspaceMembershipProvider) -> None:
        self._provider = workspace_membership_provider

    async def has_permission(
        self, user_id: str, workspace_id: str, permission: str
    ) -> bool:
        return await self._provider.has_permission(
            workspace_id=workspace_id,
            user_id=user_id,
            permission=permission,
        )

    async def require_permission(
        self, user_id: str, workspace_id: str, permission: str
    ) -> None:
        if not await self.has_permission(
            user_id=user_id, workspace_id=workspace_id, permission=permission
        ):
            raise InsufficientAnalyticsPermissionsException(
                permission=permission, workspace_id=workspace_id, user_id=user_id
            )

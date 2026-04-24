from __future__ import annotations

from app.context.organization.application.ports.integration.outboard.organization_permission_provider import (
    OrganizationPermissionProvider,
)
from app.context.workspace.application.ports.integration.inboard.organization_permission_checker_port import (
    OrganizationPermissionCheckerPort,
)


class OrganizationPermissionCheckerAdapter(OrganizationPermissionCheckerPort):
    """
    Реализация OrganizationPermissionCheckerPort для Workspace BC.

    Делегирует в OrganizationPermissionProvider (outboard Organization BC),
    инкапсулируя wildcard-логику орг-разрешений.
    """

    def __init__(self, org_permission_provider: OrganizationPermissionProvider) -> None:
        self._provider = org_permission_provider

    async def has_permission(self, user_id: str, org_id: str, permission: str) -> bool:
        return await self._provider.has_permission(
            user_id=user_id,
            org_id=org_id,
            permission=permission,
        )

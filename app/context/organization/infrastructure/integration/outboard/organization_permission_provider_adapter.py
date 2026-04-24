from __future__ import annotations

from app.context.organization.application.ports.authorization.org_permission_checker_port import (
    OrgPermissionCheckerPort,
)
from app.context.organization.application.ports.integration.outboard.organization_permission_provider import (
    OrganizationPermissionProvider,
)
from app.shared.domain.value_objects.id_vo import Id


class OrganizationPermissionProviderAdapter(OrganizationPermissionProvider):
    """
    Реализация OrganizationPermissionProvider (outboard).

    Делегирует проверку во внутренний OrgPermissionCheckerPort,
    инкапсулируя wildcard-логику и конвертацию str → Id.
    """

    def __init__(self, permission_checker: OrgPermissionCheckerPort) -> None:
        self._checker = permission_checker

    async def has_permission(self, user_id: str, org_id: str, permission: str) -> bool:
        return await self._checker.has_permission(
            user_id=Id.from_string(user_id),
            org_id=Id.from_string(org_id),
            permission=permission,
        )

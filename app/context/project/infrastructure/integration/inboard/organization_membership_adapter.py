from __future__ import annotations

from app.context.organization.application.ports.integration.outboard.organization_membership_provider import (
    OrganizationMembershipProvider,
)
from app.context.project.application.ports.integration.inboard.organization_membership_port import (
    OrganizationMembershipPort,
)


class OrganizationMembershipAdapter(OrganizationMembershipPort):
    """
    Реализация OrganizationMembershipPort для Project BC.

    Делегирует в OrganizationMembershipProvider (outboard Organization BC).
    """

    def __init__(self, org_membership_provider: OrganizationMembershipProvider) -> None:
        self._provider = org_membership_provider

    async def is_org_member(self, org_id: str, user_id: str) -> bool:
        return await self._provider.is_member(user_id=user_id, org_id=org_id)

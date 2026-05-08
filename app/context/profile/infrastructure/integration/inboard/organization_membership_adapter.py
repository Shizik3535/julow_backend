from __future__ import annotations

from app.context.organization.application.ports.integration.outboard.organization_membership_provider import (
    OrganizationMembershipProvider,
)
from app.context.profile.application.ports.integration.inboard.organization_membership_port import (
    OrganizationMembershipPort,
)


class OrganizationMembershipAdapter(OrganizationMembershipPort):
    """
    Реализация OrganizationMembershipPort для Profile BC.

    Делегирует в OrganizationMembershipProvider (Organization BC outboard).
    """

    def __init__(self, org_membership_provider: OrganizationMembershipProvider) -> None:
        self._provider = org_membership_provider

    async def is_member(self, user_id: str, organization_id: str) -> bool:
        return await self._provider.is_member(user_id=user_id, org_id=organization_id)

    async def share_organization(self, user_id_a: str, user_id_b: str) -> bool:
        if user_id_a == user_id_b:
            return True
        orgs_a = set(await self._provider.get_user_organization_ids(user_id=user_id_a))
        if not orgs_a:
            return False
        orgs_b = set(await self._provider.get_user_organization_ids(user_id=user_id_b))
        return bool(orgs_a & orgs_b)

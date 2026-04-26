from __future__ import annotations

from typing import Any

from app.context.organization.application.ports.integration.outboard.organization_membership_provider import (
    OrganizationMembershipProvider,
)
from app.context.workspace.application.ports.integration.inboard.organization_membership_port import (
    OrganizationMembershipPort,
)


class OrganizationMembershipAdapter(OrganizationMembershipPort):
    """Реализация OrganizationMembershipPort (inboard) — делегирует в OrganizationMembershipProvider из Organization BC."""

    def __init__(self, org_membership_provider: OrganizationMembershipProvider) -> None:
        self._provider = org_membership_provider

    async def is_org_member(self, org_id: str, user_id: str) -> bool:
        return await self._provider.is_member(user_id=user_id, org_id=org_id)

    async def get_org_members(self, org_id: str) -> list[dict[str, Any]]:
        dtos = await self._provider.get_members(org_id=org_id)
        return [
            {
                "id": dto.id,
                "user_id": dto.user_id,
                "display_name": dto.display_name,
                "role_id": dto.role_id,
                "joined_at": dto.joined_at.isoformat() if dto.joined_at else None,
                "is_active": dto.is_active,
                "invited_by": dto.invited_by,
            }
            for dto in dtos
        ]

    async def org_exists(self, org_id: str) -> bool:
        return await self._provider.org_exists(org_id=org_id)

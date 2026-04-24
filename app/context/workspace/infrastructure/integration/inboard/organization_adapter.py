from __future__ import annotations

from typing import Any

from app.context.organization.application.ports.integration.outboard.organization_provider import (
    OrganizationProvider,
)
from app.context.workspace.application.ports.integration.inboard.organization_port import (
    OrganizationPort,
)


class OrganizationAdapter(OrganizationPort):
    """Реализация OrganizationPort (inboard) — делегирует в OrganizationProvider из Organization BC."""

    def __init__(self, organization_provider: OrganizationProvider) -> None:
        self._provider = organization_provider

    async def org_exists(self, org_id: str) -> bool:
        return await self._provider.organization_exists(org_id=org_id)

    async def get_organization(self, org_id: str) -> dict[str, Any] | None:
        dto = await self._provider.get_organization(org_id=org_id)
        if dto is None:
            return None
        return {
            "id": dto.id,
            "name": dto.name,
            "status": dto.status,
        }

from __future__ import annotations

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.dto.organization_dto import OrganizationDTO
from app.context.organization.application.ports.integration.outboard.organization_provider import (
    OrganizationProvider,
)
from app.context.organization.domain.repositories.organization_repository import OrganizationRepository


class OrganizationProviderAdapter(OrganizationProvider):
    """Реализация OrganizationProvider (outboard) — предоставляет данные организаций другим BC."""

    def __init__(self, repo: OrganizationRepository) -> None:
        self._repo = repo

    async def get_organization(self, org_id: str) -> OrganizationDTO | None:
        aggregate = await self._repo.get_by_id(Id.from_string(org_id))
        if aggregate is None:
            return None
        return OrganizationDTO(
            id=str(aggregate.id),
            name=aggregate.name,
            status=aggregate.status.value,
            owner_ids=[str(oid) for oid in aggregate.owner_ids],
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,
        )

    async def organization_exists(self, org_id: str) -> bool:
        aggregate = await self._repo.get_by_id(Id.from_string(org_id))
        return aggregate is not None

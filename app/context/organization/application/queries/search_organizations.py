from __future__ import annotations

from typing import Any

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.context.organization.application.dto.organization_dto import OrganizationDTO, OrganizationListDTO
from app.context.organization.domain.repositories.organization_repository import OrganizationRepository


class SearchOrganizationsQuery(BaseQuery):
    """
    Запрос поиска организаций с фильтрацией.

    Атрибуты:
        offset: Смещение.
        limit: Лимит.
        filters: Опциональные фильтры.
    """

    offset: int = 0
    limit: int = 100
    filters: dict[str, Any] | None = None


class SearchOrganizationsHandler(BaseQueryHandler[SearchOrganizationsQuery, OrganizationListDTO]):
    """Обработчик поиска организаций."""

    def __init__(self, org_repo: OrganizationRepository) -> None:
        super().__init__()
        self._org_repo = org_repo

    async def handle(self, query: SearchOrganizationsQuery) -> OrganizationListDTO:
        orgs = await self._org_repo.search(
            offset=query.offset,
            limit=query.limit,
            filters=query.filters,
        )

        items = [
            OrganizationDTO(
                id=str(org.id),
                name=org.name,
                status=org.status.value,
                owner_ids=[str(oid) for oid in org.owner_ids],
                created_at=org.created_at,
                updated_at=org.updated_at,
            )
            for org in orgs
        ]
        return OrganizationListDTO(items=items, total=len(items))

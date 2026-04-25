from __future__ import annotations

from typing import Any

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.dto.organization_dto import OrganizationDTO, OrganizationListDTO
from app.context.organization.application.ports.authorization.org_permission_checker_port import OrgPermissionCheckerPort
from app.context.organization.domain.repositories.organization_repository import OrganizationRepository


class SearchOrganizationsQuery(BaseQuery):
    """
    Запрос поиска организаций.

    Атрибуты:
        caller_id: ID вызывающего пользователя.
        offset: Смещение пагинации.
        limit: Размер страницы.
        filters: Фильтры поиска.
    """

    caller_id: str
    offset: int = 0
    limit: int = 100
    filters: dict[str, Any] | None = None


class SearchOrganizationsHandler(BaseQueryHandler[SearchOrganizationsQuery, OrganizationListDTO]):
    """Обработчик поиска организаций."""

    def __init__(self, org_repo: OrganizationRepository, org_permission_checker: OrgPermissionCheckerPort) -> None:
        super().__init__()
        self._org_repo = org_repo
        self._org_permission_checker = org_permission_checker

    async def handle(self, query: SearchOrganizationsQuery) -> OrganizationListDTO:
        caller_id = Id.from_string(query.caller_id)

        orgs = await self._org_repo.search(
            offset=query.offset,
            limit=query.limit,
            filters=query.filters,
        )

        # Filter to orgs where caller has read access
        accessible_orgs = []
        for org in orgs:
            if await self._org_permission_checker.has_permission(caller_id, org.id, "org.read"):
                accessible_orgs.append(org)

        items = [
            OrganizationDTO(
                id=str(org.id),
                name=org.name,
                status=org.status.value,
                owner_ids=[str(oid) for oid in org.owner_ids],
                created_at=org.created_at,
                updated_at=org.updated_at,
            )
            for org in accessible_orgs
        ]
        return OrganizationListDTO(items=items, total=len(items))

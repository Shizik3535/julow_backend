from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.dto.organization_dto import OrganizationDTO, OrganizationListDTO
from app.context.organization.domain.repositories.organization_repository import OrganizationRepository


class GetOrganizationsByOwnerQuery(BaseQuery):
    """
    Запрос организаций по ID владельца.

    Атрибуты:
        owner_id: ID владельца.
    """

    owner_id: str


class GetOrganizationsByOwnerHandler(BaseQueryHandler[GetOrganizationsByOwnerQuery, OrganizationListDTO]):
    """Обработчик запроса организаций по владельцу."""

    def __init__(self, org_repo: OrganizationRepository) -> None:
        super().__init__()
        self._org_repo = org_repo

    async def handle(self, query: GetOrganizationsByOwnerQuery) -> OrganizationListDTO:
        orgs = await self._org_repo.get_by_owner(Id.from_string(query.owner_id))

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

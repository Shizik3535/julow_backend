from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.dto.org_role_dto import OrgRoleDTO, OrgRoleListDTO
from app.context.organization.domain.repositories.org_role_repository import OrgRoleRepository


class GetOrgRolesQuery(BaseQuery):
    """
    Запрос ролей организации.

    Атрибуты:
        org_id: ID организации.
        system_only: Только системные роли.
    """

    org_id: str
    system_only: bool = False


class GetOrgRolesHandler(BaseQueryHandler[GetOrgRolesQuery, OrgRoleListDTO]):
    """Обработчик запроса ролей организации."""

    def __init__(self, role_repo: OrgRoleRepository) -> None:
        super().__init__()
        self._role_repo = role_repo

    async def handle(self, query: GetOrgRolesQuery) -> OrgRoleListDTO:
        if query.system_only:
            roles = await self._role_repo.get_system_roles()
        else:
            roles = await self._role_repo.get_by_org(Id.from_string(query.org_id))

        items = [
            OrgRoleDTO(
                id=str(r.id),
                org_id=str(r.org_id) if r.org_id else "",
                name=r.name,
                permissions=r.permissions,
                is_system=r.is_system,
                description=r.description,
                scope=r.scope.value,
                created_at=r.created_at,
                updated_at=r.updated_at,
            )
            for r in roles
        ]
        return OrgRoleListDTO(items=items, total=len(items))

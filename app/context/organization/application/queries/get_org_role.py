from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.dto.org_role_dto import OrgRoleDTO
from app.context.organization.domain.exceptions.org_role_exceptions import OrgRoleNotFoundException
from app.context.organization.domain.repositories.org_role_repository import OrgRoleRepository


class GetOrgRoleQuery(BaseQuery):
    """
    Запрос роли по ID.

    Атрибуты:
        role_id: Идентификатор роли.
    """

    role_id: str


class GetOrgRoleHandler(BaseQueryHandler[GetOrgRoleQuery, OrgRoleDTO]):
    """Обработчик запроса роли по ID."""

    def __init__(self, role_repo: OrgRoleRepository) -> None:
        super().__init__()
        self._role_repo = role_repo

    async def handle(self, query: GetOrgRoleQuery) -> OrgRoleDTO:
        role = await self._role_repo.get_by_id(Id.from_string(query.role_id))
        if role is None:
            raise OrgRoleNotFoundException(query.role_id)

        return OrgRoleDTO(
            id=str(role.id),
            org_id=str(role.org_id) if role.org_id else "",
            name=role.name,
            permissions=role.permissions,
            is_system=role.is_system,
            description=role.description,
            scope=role.scope.value,
            created_at=role.created_at,
            updated_at=role.updated_at,
        )

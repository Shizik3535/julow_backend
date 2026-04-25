from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.dto.org_role_dto import OrgRoleDTO, OrgRoleListDTO
from app.context.organization.application.ports.authorization.org_permission_checker_port import OrgPermissionCheckerPort
from app.context.organization.domain.exceptions.organization_exceptions import OrganizationNotFoundException
from app.context.organization.domain.repositories.org_role_repository import OrgRoleRepository
from app.context.organization.domain.repositories.organization_repository import OrganizationRepository


class GetOrgRolesQuery(BaseQuery):
    """
    Запрос ролей организации.

    Атрибуты:
        org_id: ID организации.
        system_only: Только системные роли.
    """

    caller_id: str
    org_id: str
    system_only: bool = False


class GetOrgRolesHandler(BaseQueryHandler[GetOrgRolesQuery, OrgRoleListDTO]):
    """Обработчик запроса ролей организации."""

    REQUIRED_PERMISSION = "roles.read"

    def __init__(self, role_repo: OrgRoleRepository, org_repo: OrganizationRepository, org_permission_checker: OrgPermissionCheckerPort) -> None:
        super().__init__()
        self._role_repo = role_repo
        self._org_repo = org_repo
        self._org_permission_checker = org_permission_checker

    async def handle(self, query: GetOrgRolesQuery) -> OrgRoleListDTO:
        org_id = Id.from_string(query.org_id)

        org = await self._org_repo.get_by_id(org_id)
        if org is None:
            raise OrganizationNotFoundException(query.org_id)
        await self._org_permission_checker.require_permission(
            Id.from_string(query.caller_id), org_id, self.REQUIRED_PERMISSION,
        )

        if query.system_only:
            roles = await self._role_repo.get_system_roles()
        else:
            roles = await self._role_repo.get_by_org(org_id)

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

from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.dto.org_member_dto import OrgMemberDTO, OrgMemberListDTO
from app.context.organization.application.ports.authorization.org_permission_checker_port import OrgPermissionCheckerPort
from app.context.organization.domain.exceptions.organization_exceptions import OrganizationNotFoundException
from app.context.organization.domain.repositories.org_membership_repository import OrgMembershipRepository
from app.context.organization.domain.repositories.organization_repository import OrganizationRepository


class GetOrgMembersQuery(BaseQuery):
    """
    Запрос списка участников организации.

    Атрибуты:
        org_id: ID организации.
    """

    caller_id: str
    org_id: str


class GetOrgMembersHandler(BaseQueryHandler[GetOrgMembersQuery, OrgMemberListDTO]):
    """Обработчик запроса списка участников."""

    REQUIRED_PERMISSION = "members.read"

    def __init__(self, membership_repo: OrgMembershipRepository, org_repo: OrganizationRepository, org_permission_checker: OrgPermissionCheckerPort) -> None:
        super().__init__()
        self._membership_repo = membership_repo
        self._org_repo = org_repo
        self._org_permission_checker = org_permission_checker

    async def handle(self, query: GetOrgMembersQuery) -> OrgMemberListDTO:
        org_id = Id.from_string(query.org_id)

        org = await self._org_repo.get_by_id(org_id)
        if org is None:
            raise OrganizationNotFoundException(query.org_id)
        await self._org_permission_checker.require_permission(
            Id.from_string(query.caller_id), org_id, self.REQUIRED_PERMISSION,
        )

        members = await self._membership_repo.get_members_by_org(org_id)

        items = [
            OrgMemberDTO(
                id=str(m.id),
                user_id=str(m.user_id),
                display_name=m.display_name,
                role_id=str(m.role_id),
                joined_at=m.joined_at,
                is_active=m.is_active,
                invited_by=str(m.invited_by) if m.invited_by else None,
            )
            for m in members
        ]
        return OrgMemberListDTO(items=items, total=len(items))

from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.dto.org_member_dto import OrgMemberDTO
from app.context.organization.application.ports.authorization.org_permission_checker_port import OrgPermissionCheckerPort
from app.context.organization.domain.exceptions.org_membership_exceptions import OrgMemberNotFoundException
from app.context.organization.domain.repositories.org_membership_repository import OrgMembershipRepository


class GetOrgMemberQuery(BaseQuery):
    """
    Запрос участника организации по org_id и user_id.

    Атрибуты:
        org_id: ID организации.
        user_id: ID пользователя.
    """

    caller_id: str
    org_id: str
    user_id: str


class GetOrgMemberHandler(BaseQueryHandler[GetOrgMemberQuery, OrgMemberDTO]):
    """Обработчик запроса участника организации."""

    REQUIRED_PERMISSION = "members.read"

    def __init__(self, membership_repo: OrgMembershipRepository, org_permission_checker: OrgPermissionCheckerPort) -> None:
        super().__init__()
        self._membership_repo = membership_repo
        self._org_permission_checker = org_permission_checker

    async def handle(self, query: GetOrgMemberQuery) -> OrgMemberDTO:
        member = await self._membership_repo.get_member_by_org_and_user(
            org_id=Id.from_string(query.org_id),
            user_id=Id.from_string(query.user_id),
        )
        if member is None:
            raise OrgMemberNotFoundException(id=query.user_id)

        await self._org_permission_checker.require_permission(
            Id.from_string(query.caller_id), Id.from_string(query.org_id), self.REQUIRED_PERMISSION,
        )

        return OrgMemberDTO(
            id=str(member.id),
            user_id=str(member.user_id),
            display_name=member.display_name,
            role_id=str(member.role_id),
            joined_at=member.joined_at,
            is_active=member.is_active,
            invited_by=str(member.invited_by) if member.invited_by else None,
        )

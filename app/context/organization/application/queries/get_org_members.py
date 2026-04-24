from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.dto.org_member_dto import OrgMemberDTO, OrgMemberListDTO
from app.context.organization.domain.repositories.org_membership_repository import OrgMembershipRepository


class GetOrgMembersQuery(BaseQuery):
    """
    Запрос списка участников организации.

    Атрибуты:
        org_id: ID организации.
    """

    org_id: str


class GetOrgMembersHandler(BaseQueryHandler[GetOrgMembersQuery, OrgMemberListDTO]):
    """Обработчик запроса списка участников."""

    def __init__(self, membership_repo: OrgMembershipRepository) -> None:
        super().__init__()
        self._membership_repo = membership_repo

    async def handle(self, query: GetOrgMembersQuery) -> OrgMemberListDTO:
        members = await self._membership_repo.get_members_by_org(Id.from_string(query.org_id))

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

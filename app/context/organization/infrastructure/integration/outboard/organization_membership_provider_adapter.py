from __future__ import annotations

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.dto.org_member_dto import OrgMemberDTO
from app.context.organization.application.ports.integration.outboard.organization_membership_provider import (
    OrganizationMembershipProvider,
)
from app.context.organization.domain.repositories.org_membership_repository import OrgMembershipRepository


class OrganizationMembershipProviderAdapter(OrganizationMembershipProvider):
    """Реализация OrganizationMembershipProvider (outboard) — предоставляет данные о членстве другим BC."""

    def __init__(self, repo: OrgMembershipRepository) -> None:
        self._repo = repo

    async def is_member(self, user_id: str, org_id: str) -> bool:
        member = await self._repo.get_member_by_org_and_user(
            org_id=Id.from_string(org_id),
            user_id=Id.from_string(user_id),
        )
        return member is not None and member.is_active

    async def get_member_role(self, user_id: str, org_id: str) -> str | None:
        member = await self._repo.get_member_by_org_and_user(
            org_id=Id.from_string(org_id),
            user_id=Id.from_string(user_id),
        )
        if member is None:
            return None
        return str(member.role_id)

    async def get_members(self, org_id: str) -> list[OrgMemberDTO]:
        members = await self._repo.get_members_by_org(Id.from_string(org_id))
        return [
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

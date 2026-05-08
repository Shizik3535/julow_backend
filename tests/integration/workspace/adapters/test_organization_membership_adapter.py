"""
Интеграционные тесты OrganizationMembershipAdapter (inboard).

Адаптер делегирует в OrganizationMembershipProvider (outboard Organization BC).
Тестируем через stub provider, проверяя корректность маппинга DTO → dict.
"""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.dto.org_member_dto import OrgMemberDTO
from app.context.organization.application.ports.integration.outboard.organization_membership_provider import (
    OrganizationMembershipProvider,
)
from app.context.workspace.infrastructure.integration.inboard.organization_membership_adapter import (
    OrganizationMembershipAdapter,
)


class _StubOrgMembershipProvider(OrganizationMembershipProvider):
    """Stub outboard-провайдер Organization Membership."""

    def __init__(self, members: dict[str, list[OrgMemberDTO]] | None = None):
        self._members = members or {}

    async def is_member(self, user_id: str, org_id: str) -> bool:
        org_members = self._members.get(org_id, [])
        return any(m.user_id == user_id for m in org_members)

    async def get_member_role(self, user_id: str, org_id: str) -> str | None:
        org_members = self._members.get(org_id, [])
        for m in org_members:
            if m.user_id == user_id:
                return m.role_id
        return None

    async def get_members(self, org_id: str) -> list[OrgMemberDTO]:
        return self._members.get(org_id, [])

    async def org_exists(self, org_id: str) -> bool:
        return org_id in self._members

    async def get_user_organization_ids(self, user_id: str) -> list[str]:
        return [
            org_id
            for org_id, members in self._members.items()
            if any(m.user_id == user_id and m.is_active for m in members)
        ]


def _make_org_member_dto(user_id: str, role_id: str = "member-role") -> OrgMemberDTO:
    from datetime import datetime, timezone
    return OrgMemberDTO(
        id=str(Id.generate()),
        user_id=user_id,
        display_name=None,
        role_id=role_id,
        joined_at=datetime.now(tz=timezone.utc),
        is_active=True,
        invited_by=None,
    )


@pytest.mark.integration
class TestOrganizationMembershipAdapter:
    """Тесты OrganizationMembershipAdapter."""

    async def test_is_org_member_true(self) -> None:
        uid = str(Id.generate())
        oid = str(Id.generate())
        provider = _StubOrgMembershipProvider({oid: [_make_org_member_dto(uid)]})
        adapter = OrganizationMembershipAdapter(org_membership_provider=provider)

        result = await adapter.is_org_member(org_id=oid, user_id=uid)
        assert result is True

    async def test_is_org_member_false(self) -> None:
        uid = str(Id.generate())
        oid = str(Id.generate())
        provider = _StubOrgMembershipProvider({})
        adapter = OrganizationMembershipAdapter(org_membership_provider=provider)

        result = await adapter.is_org_member(org_id=oid, user_id=uid)
        assert result is False

    async def test_get_org_members(self) -> None:
        oid = str(Id.generate())
        member1 = _make_org_member_dto(str(Id.generate()))
        member2 = _make_org_member_dto(str(Id.generate()))
        provider = _StubOrgMembershipProvider({oid: [member1, member2]})
        adapter = OrganizationMembershipAdapter(org_membership_provider=provider)

        result = await adapter.get_org_members(oid)
        assert len(result) == 2
        assert all(isinstance(m, dict) for m in result)

    async def test_get_org_members_empty(self) -> None:
        oid = str(Id.generate())
        provider = _StubOrgMembershipProvider({})
        adapter = OrganizationMembershipAdapter(org_membership_provider=provider)

        result = await adapter.get_org_members(oid)
        assert result == []

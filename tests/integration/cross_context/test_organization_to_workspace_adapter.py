"""
Cross-context: Organization → Workspace.
Тестируем OrganizationAdapter и OrganizationMembershipAdapter
через реальные Organization BC репозитории.
"""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.infrastructure.integration.inboard.organization_adapter import (
    OrganizationAdapter,
)
from app.context.workspace.infrastructure.integration.inboard.organization_membership_adapter import (
    OrganizationMembershipAdapter,
)
from app.context.organization.application.dto.organization_dto import OrganizationDTO
from app.context.organization.application.dto.org_member_dto import OrgMemberDTO
from app.context.organization.application.ports.integration.outboard.organization_provider import (
    OrganizationProvider,
)
from app.context.organization.application.ports.integration.outboard.organization_membership_provider import (
    OrganizationMembershipProvider,
)
from datetime import datetime, timezone


class _RealOrgProvider(OrganizationProvider):
    def __init__(self, org_repo):
        self._org_repo = org_repo

    async def get_organization(self, org_id: str) -> OrganizationDTO | None:
        from app.shared.domain.value_objects.id_vo import Id as IdVO
        org = await self._org_repo.get_by_id(IdVO.from_string(org_id))
        if org is None:
            return None
        return OrganizationDTO(
            id=str(org.id),
            name=org.name,
            status=org.status.value if hasattr(org.status, "value") else str(org.status),
            owner_ids=[str(oid) for oid in org.owner_ids],
            personalization={},
            security_policy={},
            membership_policy={},
            created_at=datetime.now(tz=timezone.utc),
            updated_at=datetime.now(tz=timezone.utc),
        )

    async def organization_exists(self, org_id: str) -> bool:
        from app.shared.domain.value_objects.id_vo import Id as IdVO
        return await self._org_repo.get_by_id(IdVO.from_string(org_id)) is not None


class _RealOrgMembershipProvider(OrganizationMembershipProvider):
    def __init__(self, membership_repo):
        self._membership_repo = membership_repo

    async def is_member(self, user_id: str, org_id: str) -> bool:
        from app.shared.domain.value_objects.id_vo import Id as IdVO
        membership = await self._membership_repo.get_by_org_id(IdVO.from_string(org_id))
        if membership is None:
            return False
        return any(m.user_id == IdVO.from_string(user_id) for m in membership.members)

    async def get_member_role(self, user_id: str, org_id: str) -> str | None:
        from app.shared.domain.value_objects.id_vo import IdVO
        membership = await self._membership_repo.get_by_org_id(IdVO.from_string(org_id))
        if membership is None:
            return None
        for m in membership.members:
            if m.user_id == IdVO.from_string(user_id):
                return str(m.role_id)
        return None

    async def get_members(self, org_id: str) -> list[OrgMemberDTO]:
        from app.shared.domain.value_objects.id_vo import Id as IdVO
        membership = await self._membership_repo.get_by_org_id(IdVO.from_string(org_id))
        if membership is None:
            return []
        return [
            OrgMemberDTO(
                id=str(m.id),
                user_id=str(m.user_id),
                display_name=None,
                role_id=str(m.role_id),
                joined_at=datetime.now(tz=timezone.utc),
                is_active=m.is_active,
                invited_by=None,
            )
            for m in membership.members
        ]

    async def org_exists(self, org_id: str) -> bool:
        from app.shared.domain.value_objects.id_vo import Id as IdVO
        membership = await self._membership_repo.get_by_org_id(IdVO.from_string(org_id))
        return membership is not None

    async def get_user_organization_ids(self, user_id: str) -> list[str]:
        from app.shared.domain.value_objects.id_vo import Id as IdVO
        memberships = await self._membership_repo.get_by_user_id(IdVO.from_string(user_id))
        target = IdVO.from_string(user_id)
        result: list[str] = []
        for ms in memberships:
            if any(m.user_id == target and m.is_active for m in ms.members):
                result.append(str(ms.org_id))
        return result


@pytest.mark.integration
class TestOrganizationAdapterCrossContext:
    """Cross-context: Organization → Workspace через реальные Organization BC."""

    async def test_org_exists_with_real_org(self, org_repo, make_org) -> None:
        org = await make_org()
        provider = _RealOrgProvider(org_repo)
        adapter = OrganizationAdapter(organization_provider=provider)

        result = await adapter.org_exists(str(org.id))
        assert result is True

    async def test_get_organization_with_real_org(self, org_repo, make_org) -> None:
        org = await make_org(name="Cross Org")
        provider = _RealOrgProvider(org_repo)
        adapter = OrganizationAdapter(organization_provider=provider)

        result = await adapter.get_organization(str(org.id))
        assert result is not None
        assert result["name"] == "Cross Org"


@pytest.mark.integration
class TestOrgMembershipAdapterCrossContext:
    """Cross-context: OrganizationMembership → Workspace через реальные Organization BC."""

    async def test_is_org_member_with_real_data(
        self, membership_repo, make_org_with_membership
    ) -> None:
        data = await make_org_with_membership()
        org = data["org"]
        owner_id = data["owner_id"]

        provider = _RealOrgMembershipProvider(membership_repo)
        adapter = OrganizationMembershipAdapter(org_membership_provider=provider)

        result = await adapter.is_org_member(org_id=str(org.id), user_id=str(owner_id))
        assert result is True

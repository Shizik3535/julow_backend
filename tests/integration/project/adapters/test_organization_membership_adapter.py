"""Интеграционные тесты OrganizationMembershipAdapter (реальные repos)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.infrastructure.integration.inboard.organization_membership_adapter import (
    OrganizationMembershipAdapter,
)


class _StubOrgMembershipProvider:
    """Stub OrganizationMembershipProvider для тестов."""

    def __init__(self, is_member: bool = True):
        self._is_member = is_member

    async def is_member(self, user_id: str, org_id: str) -> bool:
        return self._is_member
    
    async def org_exists(self, org_id: str) -> bool:
        return True


@pytest.mark.integration
class TestOrganizationMembershipAdapter:
    """Тесты OrganizationMembershipAdapter — inboard adapter."""

    async def test_is_org_member_true(self) -> None:
        provider = _StubOrgMembershipProvider(is_member=True)
        adapter = OrganizationMembershipAdapter(org_membership_provider=provider)
        result = await adapter.is_org_member(str(Id.generate()), str(Id.generate()))
        assert result is True

    async def test_is_org_member_false(self) -> None:
        provider = _StubOrgMembershipProvider(is_member=False)
        adapter = OrganizationMembershipAdapter(org_membership_provider=provider)
        result = await adapter.is_org_member(str(Id.generate()), str(Id.generate()))
        assert result is False

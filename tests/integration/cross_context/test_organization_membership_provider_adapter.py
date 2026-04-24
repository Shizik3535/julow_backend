"""Cross-context: OrganizationMembershipProviderAdapter — предоставляет данные о членстве другим BC."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.infrastructure.integration.outboard.organization_membership_provider_adapter import (
    OrganizationMembershipProviderAdapter,
)


@pytest.mark.integration
class TestOrganizationMembershipProviderAdapter:
    @pytest.fixture
    def adapter(self, membership_repo):
        return OrganizationMembershipProviderAdapter(repo=membership_repo)

    async def test_is_member(self, adapter, make_org_with_membership) -> None:
        data = await make_org_with_membership()
        result = await adapter.is_member(str(data["owner_id"]), str(data["org"].id))
        assert result is True

    async def test_is_member_false_for_unknown(self, adapter, make_org_with_membership) -> None:
        data = await make_org_with_membership()
        result = await adapter.is_member(str(Id.generate()), str(data["org"].id))
        assert result is False

    async def test_get_member_role(self, adapter, make_org_with_membership) -> None:
        data = await make_org_with_membership()
        role_id = await adapter.get_member_role(str(data["owner_id"]), str(data["org"].id))
        assert role_id is not None

    async def test_get_members(self, adapter, make_org_with_membership) -> None:
        data = await make_org_with_membership()
        members = await adapter.get_members(str(data["org"].id))
        assert len(members) >= 1

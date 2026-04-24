"""Cross-context: OrganizationPermissionProviderAdapter — делегирует проверку разрешений."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.infrastructure.integration.outboard.organization_permission_provider_adapter import (
    OrganizationPermissionProviderAdapter,
)
from app.context.organization.infrastructure.authorization.org_role_based_permission_checker import (
    OrgRoleBasedPermissionChecker,
)


@pytest.mark.integration
class TestOrganizationPermissionProviderAdapter:
    @pytest.fixture
    def adapter(self, membership_repo, org_role_repo):
        checker = OrgRoleBasedPermissionChecker(
            membership_repo=membership_repo,
            org_role_repo=org_role_repo,
        )
        return OrganizationPermissionProviderAdapter(permission_checker=checker)

    async def test_has_permission_owner(self, adapter, make_org_with_membership) -> None:
        data = await make_org_with_membership()
        result = await adapter.has_permission(str(data["owner_id"]), str(data["org"].id), "members.write")
        assert result is True

    async def test_has_permission_non_member(self, adapter, make_org_with_membership) -> None:
        data = await make_org_with_membership()
        result = await adapter.has_permission(str(Id.generate()), str(data["org"].id), "members.write")
        assert result is False

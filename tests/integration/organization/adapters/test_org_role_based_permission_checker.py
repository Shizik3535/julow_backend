"""Интеграционные тесты OrgRoleBasedPermissionChecker (реальная БД)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.exceptions.authorization_exceptions import (
    InsufficientOrgPermissionsException,
)
from app.context.organization.infrastructure.authorization.org_role_based_permission_checker import (
    OrgRoleBasedPermissionChecker,
)


@pytest.mark.integration
class TestOrgRoleBasedPermissionChecker:
    """Тесты проверки разрешений на основе орг-роли."""

    @pytest.fixture
    def checker(self, membership_repo, org_role_repo) -> OrgRoleBasedPermissionChecker:
        return OrgRoleBasedPermissionChecker(
            membership_repo=membership_repo,
            org_role_repo=org_role_repo,
        )

    async def test_has_permission_exact_match(self, checker, make_org_with_membership) -> None:
        data = await make_org_with_membership()
        # owner role has "org.*" which covers everything
        result = await checker.has_permission(data["owner_id"], data["org"].id, "members.write")
        assert result is True

    async def test_has_permission_wildcard_org(self, checker, make_org_with_membership) -> None:
        data = await make_org_with_membership()
        result = await checker.has_permission(data["owner_id"], data["org"].id, "anything.anything")
        assert result is True

    async def test_has_permission_wildcard_group(
        self, checker, make_org_with_membership, make_org_role, membership_repo
    ) -> None:
        data = await make_org_with_membership()
        member_user_id = Id.generate()
        admin_role = await make_org_role(
            org_id=data["org"].id,
            name="test-admin",
            permissions=["members.*"],
        )
        membership = data["membership"]
        membership.add_member(user_id=member_user_id, role_id=admin_role.id)
        membership.clear_domain_events()
        await membership_repo.update(membership)

        result = await checker.has_permission(member_user_id, data["org"].id, "members.write")
        assert result is True

    async def test_has_permission_no_match(
        self, checker, make_org_with_membership, make_org_role, membership_repo
    ) -> None:
        data = await make_org_with_membership()
        member_user_id = Id.generate()
        member_role = await make_org_role(
            org_id=data["org"].id,
            name="limited-role",
            permissions=["self.*"],
        )
        membership = data["membership"]
        membership.add_member(user_id=member_user_id, role_id=member_role.id)
        membership.clear_domain_events()
        await membership_repo.update(membership)

        result = await checker.has_permission(member_user_id, data["org"].id, "members.write")
        assert result is False

    async def test_has_permission_inactive_member(
        self, checker, make_org_with_membership, membership_repo
    ) -> None:
        data = await make_org_with_membership()
        member_user_id = Id.generate()
        membership = data["membership"]
        membership.add_member(user_id=member_user_id, role_id=data["owner_role"].id)
        membership.clear_domain_events()
        await membership_repo.update(membership)

        membership.deactivate_member(user_id=member_user_id, is_owner=False)
        membership.clear_domain_events()
        await membership_repo.update(membership)

        result = await checker.has_permission(member_user_id, data["org"].id, "members.write")
        assert result is False

    async def test_has_permission_not_member(self, checker, make_org_with_membership) -> None:
        data = await make_org_with_membership()
        result = await checker.has_permission(Id.generate(), data["org"].id, "members.write")
        assert result is False

    async def test_require_permission_raises(self, checker, make_org_with_membership) -> None:
        data = await make_org_with_membership()
        with pytest.raises(InsufficientOrgPermissionsException):
            await checker.require_permission(Id.generate(), data["org"].id, "members.write")

    async def test_require_permission_ok(self, checker, make_org_with_membership) -> None:
        data = await make_org_with_membership()
        # Should not raise — owner has org.*
        await checker.require_permission(data["owner_id"], data["org"].id, "members.write")

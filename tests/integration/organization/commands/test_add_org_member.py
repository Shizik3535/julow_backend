"""Интеграционные тесты AddOrgMemberHandler (реальные repos + stubs)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.commands.add_org_member import (
    AddOrgMemberCommand,
    AddOrgMemberHandler,
)
from app.context.organization.application.exceptions.membership_app_exceptions import (
    MemberAlreadyExistsException,
)


@pytest.mark.integration
class TestAddOrgMemberHandler:
    @pytest.fixture
    def handler(self, org_repo, membership_repo, org_role_repo, permission_checker_stub, identity_user_stub, event_bus_stub):
        return AddOrgMemberHandler(
            org_repo=org_repo,
            membership_repo=membership_repo,
            org_role_repo=org_role_repo,
            org_permission_checker=permission_checker_stub,
            identity_port=identity_user_stub,
            event_bus=event_bus_stub,
        )

    async def test_add_member(self, handler, make_org_with_membership, membership_repo) -> None:
        data = await make_org_with_membership()
        new_user = Id.generate()
        cmd = AddOrgMemberCommand(
            caller_id=str(Id.generate()),
            org_id=str(data["org"].id),
            user_id=str(new_user),
            role_id=str(data["owner_role"].id),
        )
        await handler.handle(cmd)
        membership = await membership_repo.get_by_org_id(data["org"].id)
        assert membership is not None
        assert any(m.user_id == new_user for m in membership.members)

    async def test_duplicate_member_raises(self, handler, make_org_with_membership) -> None:
        data = await make_org_with_membership()
        cmd = AddOrgMemberCommand(
            caller_id=str(Id.generate()),
            org_id=str(data["org"].id),
            user_id=str(data["owner_id"]),
            role_id=str(data["owner_role"].id),
        )
        with pytest.raises(MemberAlreadyExistsException):
            await handler.handle(cmd)

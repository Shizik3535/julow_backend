"""Интеграционные тесты ChangeOrgMemberRoleHandler (реальные repos + stubs)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.commands.change_org_member_role import (
    ChangeOrgMemberRoleCommand,
    ChangeOrgMemberRoleHandler,
)


@pytest.mark.integration
class TestChangeOrgMemberRoleHandler:
    @pytest.fixture
    def handler(self, membership_repo, permission_checker_stub, event_bus_stub):
        return ChangeOrgMemberRoleHandler(
            membership_repo=membership_repo,
            org_permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_change_role(self, handler, make_org_with_membership, make_org_role, membership_repo) -> None:
        data = await make_org_with_membership()
        new_user = Id.generate()
        membership = data["membership"]
        membership.add_member(user_id=new_user, role_id=data["owner_role"].id)
        membership.clear_domain_events()
        await membership_repo.update(membership)

        new_role = await make_org_role(org_id=data["org"].id, name="new-role")
        cmd = ChangeOrgMemberRoleCommand(
            caller_id=str(Id.generate()),
            org_id=str(data["org"].id),
            user_id=str(new_user),
            new_role_id=str(new_role.id),
        )
        await handler.handle(cmd)
        member = await membership_repo.get_member_by_org_and_user(data["org"].id, new_user)
        assert member is not None
        assert member.role_id == new_role.id

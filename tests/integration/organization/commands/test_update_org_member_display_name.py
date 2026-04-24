"""Интеграционные тесты UpdateOrgMemberDisplayNameHandler (реальные repos + stubs)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.commands.update_org_member_display_name import (
    UpdateOrgMemberDisplayNameCommand,
    UpdateOrgMemberDisplayNameHandler,
)


@pytest.mark.integration
class TestUpdateOrgMemberDisplayNameHandler:
    @pytest.fixture
    def handler(self, membership_repo, permission_checker_stub, event_bus_stub):
        return UpdateOrgMemberDisplayNameHandler(
            membership_repo=membership_repo,
            org_permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_update_display_name(self, handler, make_org_with_membership, membership_repo) -> None:
        data = await make_org_with_membership()
        new_user = Id.generate()
        membership = data["membership"]
        membership.add_member(user_id=new_user, role_id=data["owner_role"].id, display_name="Old")
        membership.clear_domain_events()
        await membership_repo.update(membership)

        cmd = UpdateOrgMemberDisplayNameCommand(
            caller_id=str(Id.generate()),
            org_id=str(data["org"].id),
            user_id=str(new_user),
            display_name="New Name",
        )
        await handler.handle(cmd)
        member = await membership_repo.get_member_by_org_and_user(data["org"].id, new_user)
        assert member is not None
        assert member.display_name == "New Name"

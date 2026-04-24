"""Интеграционные тесты ReactivateOrgMemberHandler (реальные repos + stubs)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.commands.reactivate_org_member import (
    ReactivateOrgMemberCommand,
    ReactivateOrgMemberHandler,
)


@pytest.mark.integration
class TestReactivateOrgMemberHandler:
    @pytest.fixture
    def handler(self, membership_repo, permission_checker_stub, event_bus_stub):
        return ReactivateOrgMemberHandler(
            membership_repo=membership_repo,
            org_permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_reactivate_member(self, handler, make_org_with_membership, membership_repo) -> None:
        data = await make_org_with_membership()
        new_user = Id.generate()
        membership = data["membership"]
        membership.add_member(user_id=new_user, role_id=data["owner_role"].id)
        membership.clear_domain_events()
        await membership_repo.update(membership)

        membership.deactivate_member(user_id=new_user, is_owner=False)
        membership.clear_domain_events()
        await membership_repo.update(membership)

        cmd = ReactivateOrgMemberCommand(
            caller_id=str(Id.generate()),
            org_id=str(data["org"].id),
            user_id=str(new_user),
        )
        await handler.handle(cmd)
        member = await membership_repo.get_member_by_org_and_user(data["org"].id, new_user)
        assert member is not None
        assert member.is_active is True

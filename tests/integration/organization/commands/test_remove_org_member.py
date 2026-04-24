"""Интеграционные тесты RemoveOrgMemberHandler (реальные repos + stubs)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.commands.remove_org_member import (
    RemoveOrgMemberCommand,
    RemoveOrgMemberHandler,
)


@pytest.mark.integration
class TestRemoveOrgMemberHandler:
    @pytest.fixture
    def handler(self, org_repo, membership_repo, permission_checker_stub, event_bus_stub):
        return RemoveOrgMemberHandler(
            org_repo=org_repo,
            membership_repo=membership_repo,
            org_permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_remove_member(self, handler, make_org_with_membership, membership_repo) -> None:
        data = await make_org_with_membership()
        new_user = Id.generate()
        membership = data["membership"]
        membership.add_member(user_id=new_user, role_id=data["owner_role"].id)
        membership.clear_domain_events()
        await membership_repo.update(membership)

        cmd = RemoveOrgMemberCommand(
            caller_id=str(Id.generate()),
            org_id=str(data["org"].id),
            user_id=str(new_user),
        )
        await handler.handle(cmd)
        found = await membership_repo.get_by_org_id(data["org"].id)
        assert found is not None
        assert not any(m.user_id == new_user for m in found.members)

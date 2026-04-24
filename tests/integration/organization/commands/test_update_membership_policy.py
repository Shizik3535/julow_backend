"""Интеграционные тесты UpdateMembershipPolicyHandler (реальные repos + stubs)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.commands.update_membership_policy import (
    UpdateMembershipPolicyCommand,
    UpdateMembershipPolicyHandler,
)


@pytest.mark.integration
class TestUpdateMembershipPolicyHandler:
    @pytest.fixture
    def handler(self, org_repo, permission_checker_stub, event_bus_stub):
        return UpdateMembershipPolicyHandler(
            org_repo=org_repo,
            org_permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_update_policy(self, handler, make_org, org_repo) -> None:
        org = await make_org()
        cmd = UpdateMembershipPolicyCommand(
            caller_id=str(Id.generate()),
            org_id=str(org.id),
            max_members=100,
            require_approval=True,
        )
        await handler.handle(cmd)
        found = await org_repo.get_by_id(org.id)
        assert found is not None
        assert found.membership_policy.max_members == 100
        assert found.membership_policy.require_approval is True

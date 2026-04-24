"""Интеграционные тесты RevokeInvitationHandler (реальные repos + stubs)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.commands.revoke_invitation import (
    RevokeInvitationCommand,
    RevokeInvitationHandler,
)
from app.context.organization.domain.value_objects.invitation_status import InvitationStatus


@pytest.mark.integration
class TestRevokeInvitationHandler:
    @pytest.fixture
    def handler(self, invitation_repo, permission_checker_stub, event_bus_stub):
        return RevokeInvitationHandler(
            invitation_repo=invitation_repo,
            org_permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_revoke(self, handler, make_invitation, invitation_repo) -> None:
        inv = await make_invitation()
        cmd = RevokeInvitationCommand(
            caller_id=str(Id.generate()),
            org_id=str(inv.org_id),
            invitation_id=str(inv.id),
        )
        await handler.handle(cmd)

        found = await invitation_repo.get_by_id(inv.id)
        assert found is not None
        assert found.status == InvitationStatus.REVOKED

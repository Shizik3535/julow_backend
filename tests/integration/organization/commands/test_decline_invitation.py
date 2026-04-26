"""Интеграционные тесты DeclineInvitationHandler (реальные repos + stubs)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.commands.decline_invitation import (
    DeclineInvitationCommand,
    DeclineInvitationHandler,
)
from app.context.organization.domain.value_objects.invitation_status import InvitationStatus
from tests.integration.organization.conftest import _StubIdentityUserPort, _AlwaysAllowPermissionChecker


@pytest.mark.integration
class TestDeclineInvitationHandler:
    @pytest.fixture
    def handler(self, invitation_repo, event_bus_stub, identity_user_stub, permission_checker_stub):
        return DeclineInvitationHandler(
            invitation_repo=invitation_repo,
            identity_port=identity_user_stub,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_decline(self, handler, make_invitation, invitation_repo) -> None:
        inv = await make_invitation()
        declining_user = inv.invited_by
        cmd = DeclineInvitationCommand(invitation_id=str(inv.id), user_id=str(declining_user))
        await handler.handle(cmd)

        found = await invitation_repo.get_by_id(inv.id)
        assert found is not None
        assert found.status == InvitationStatus.DECLINED
        assert found.user_id == declining_user

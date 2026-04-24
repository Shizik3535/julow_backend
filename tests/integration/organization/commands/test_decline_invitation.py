"""Интеграционные тесты DeclineInvitationHandler (реальные repos + stubs)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.commands.decline_invitation import (
    DeclineInvitationCommand,
    DeclineInvitationHandler,
)
from app.context.organization.domain.value_objects.invitation_status import InvitationStatus


@pytest.mark.integration
class TestDeclineInvitationHandler:
    @pytest.fixture
    def handler(self, invitation_repo, event_bus_stub):
        return DeclineInvitationHandler(
            invitation_repo=invitation_repo,
            event_bus=event_bus_stub,
        )

    async def test_decline(self, handler, make_invitation, invitation_repo) -> None:
        inv = await make_invitation()
        cmd = DeclineInvitationCommand(invitation_id=str(inv.id))
        await handler.handle(cmd)

        found = await invitation_repo.get_by_id(inv.id)
        assert found is not None
        assert found.status == InvitationStatus.DECLINED

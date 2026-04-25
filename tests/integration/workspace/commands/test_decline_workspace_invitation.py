"""Интеграционные тесты DeclineWorkspaceInvitationHandler."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.commands.decline_workspace_invitation import (
    DeclineWorkspaceInvitationCommand,
    DeclineWorkspaceInvitationHandler,
)
from app.context.workspace.domain.exceptions.workspace_invitation_exceptions import InvitationNotFoundException
from app.context.workspace.domain.value_objects.invitation_status import InvitationStatus
from tests.integration.workspace.conftest import _NoopEventBus


@pytest.mark.integration
class TestDeclineWorkspaceInvitationHandler:
    """Тесты DeclineWorkspaceInvitationHandler."""

    @pytest.fixture
    def handler(self, ws_invitation_repo) -> DeclineWorkspaceInvitationHandler:
        return DeclineWorkspaceInvitationHandler(
            invitation_repo=ws_invitation_repo,
            event_bus=_NoopEventBus(),
        )

    async def test_decline_success(self, handler, ws_invitation_repo, make_workspace_invitation) -> None:
        inv = await make_workspace_invitation()
        cmd = DeclineWorkspaceInvitationCommand(invitation_id=str(inv.id))
        await handler.handle(cmd)

        found = await ws_invitation_repo.get_by_id(inv.id)
        assert found is not None
        assert found.status == InvitationStatus.DECLINED

    async def test_decline_not_found(self, handler) -> None:
        cmd = DeclineWorkspaceInvitationCommand(invitation_id=str(Id.generate()))
        with pytest.raises(InvitationNotFoundException):
            await handler.handle(cmd)

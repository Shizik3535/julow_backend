"""Интеграционные тесты RevokeWorkspaceInvitationHandler."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.commands.revoke_workspace_invitation import (
    RevokeWorkspaceInvitationCommand,
    RevokeWorkspaceInvitationHandler,
)
from app.context.workspace.domain.exceptions.workspace_invitation_exceptions import InvitationNotFoundException
from app.context.workspace.domain.value_objects.invitation_status import InvitationStatus
from tests.integration.workspace.conftest import _AlwaysAllowPermissionChecker, _NoopEventBus


@pytest.mark.integration
class TestRevokeWorkspaceInvitationHandler:
    """Тесты RevokeWorkspaceInvitationHandler."""

    @pytest.fixture
    def handler(self, ws_invitation_repo) -> RevokeWorkspaceInvitationHandler:
        return RevokeWorkspaceInvitationHandler(
            invitation_repo=ws_invitation_repo,
            permission_checker=_AlwaysAllowPermissionChecker(),
            event_bus=_NoopEventBus(),
        )

    async def test_revoke_success(self, handler, ws_invitation_repo, make_workspace_invitation) -> None:
        inv = await make_workspace_invitation()
        cmd = RevokeWorkspaceInvitationCommand(
            caller_id=str(Id.generate()),
            invitation_id=str(inv.id),
        )
        await handler.handle(cmd)

        found = await ws_invitation_repo.get_by_id(inv.id)
        assert found is not None
        assert found.status == InvitationStatus.REVOKED

    async def test_revoke_not_found(self, handler) -> None:
        cmd = RevokeWorkspaceInvitationCommand(
            caller_id=str(Id.generate()),
            invitation_id=str(Id.generate()),
        )
        with pytest.raises(InvitationNotFoundException):
            await handler.handle(cmd)

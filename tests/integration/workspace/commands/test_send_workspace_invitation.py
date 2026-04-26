"""Интеграционные тесты SendWorkspaceInvitationHandler."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.commands.send_workspace_invitation import (
    SendWorkspaceInvitationCommand,
    SendWorkspaceInvitationHandler,
)
from app.context.workspace.application.exceptions.invitation_app_exceptions import DuplicateInvitationForEmailException
from tests.integration.workspace.conftest import _AlwaysAllowPermissionChecker, _NoopEventBus


@pytest.mark.integration
class TestSendWorkspaceInvitationHandler:
    """Тесты SendWorkspaceInvitationHandler."""

    @pytest.fixture
    def handler(self, ws_invitation_repo, ws_repo) -> SendWorkspaceInvitationHandler:
        return SendWorkspaceInvitationHandler(
            invitation_repo=ws_invitation_repo,
            ws_repo=ws_repo,
            permission_checker=_AlwaysAllowPermissionChecker(),
            event_bus=_NoopEventBus(),
        )

    async def test_send_invitation_success(self, handler, ws_invitation_repo, make_workspace) -> None:
        ws = await make_workspace()
        cmd = SendWorkspaceInvitationCommand(
            caller_id=str(ws.owner_ids[0]),
            workspace_id=str(ws.id),
            email="invite@example.com",
            role_id=str(Id.generate()),
            invited_by=str(ws.owner_ids[0]),
        )
        result = await handler.handle(cmd)

        assert result.email == "invite@example.com"
        assert result.workspace_id == str(ws.id)
        assert result.status == "pending"

    async def test_send_duplicate_pending_raises(
        self, handler, ws_invitation_repo, make_workspace
    ) -> None:
        ws = await make_workspace()
        cmd = SendWorkspaceInvitationCommand(
            caller_id=str(ws.owner_ids[0]),
            workspace_id=str(ws.id),
            email="dup@example.com",
            role_id=str(Id.generate()),
            invited_by=str(ws.owner_ids[0]),
        )
        await handler.handle(cmd)

        with pytest.raises(DuplicateInvitationForEmailException):
            await handler.handle(cmd)

"""Интеграционные тесты SendBulkWorkspaceInvitationsHandler."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.commands.send_bulk_workspace_invitations import (
    SendBulkWorkspaceInvitationsCommand,
    SendBulkWorkspaceInvitationsHandler,
)
from tests.integration.workspace.conftest import _AlwaysAllowPermissionChecker, _NoopEventBus


@pytest.mark.integration
class TestSendBulkWorkspaceInvitationsHandler:
    """Тесты SendBulkWorkspaceInvitationsHandler."""

    @pytest.fixture
    def handler(self, ws_invitation_repo, ws_repo) -> SendBulkWorkspaceInvitationsHandler:
        return SendBulkWorkspaceInvitationsHandler(
            invitation_repo=ws_invitation_repo,
            ws_repo=ws_repo,
            permission_checker=_AlwaysAllowPermissionChecker(),
            event_bus=_NoopEventBus(),
        )

    async def test_bulk_send_success(self, handler, make_workspace) -> None:
        ws = await make_workspace()
        cmd = SendBulkWorkspaceInvitationsCommand(
            caller_id=str(ws.owner_ids[0]),
            workspace_id=str(ws.id),
            emails=["a@example.com", "b@example.com", "c@example.com"],
            role_id=str(Id.generate()),
            invited_by=str(ws.owner_ids[0]),
        )
        result = await handler.handle(cmd)

        assert result.total == 3
        assert len(result.items) == 3

    async def test_bulk_send_skips_duplicates(self, handler, make_workspace) -> None:
        ws = await make_workspace()
        cmd1 = SendBulkWorkspaceInvitationsCommand(
            caller_id=str(ws.owner_ids[0]),
            workspace_id=str(ws.id),
            emails=["dup@example.com"],
            role_id=str(Id.generate()),
            invited_by=str(ws.owner_ids[0]),
        )
        await handler.handle(cmd1)

        cmd2 = SendBulkWorkspaceInvitationsCommand(
            caller_id=str(ws.owner_ids[0]),
            workspace_id=str(ws.id),
            emails=["dup@example.com", "new@example.com"],
            role_id=str(Id.generate()),
            invited_by=str(ws.owner_ids[0]),
        )
        result = await handler.handle(cmd2)

        assert result.total == 1
        assert result.items[0].email == "new@example.com"

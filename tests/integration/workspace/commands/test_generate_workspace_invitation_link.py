"""Интеграционные тесты GenerateWorkspaceInvitationLinkHandler."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.commands.generate_workspace_invitation_link import (
    GenerateWorkspaceInvitationLinkCommand,
    GenerateWorkspaceInvitationLinkHandler,
)
from tests.integration.workspace.conftest import _AlwaysAllowPermissionChecker, _NoopEventBus


@pytest.mark.integration
class TestGenerateWorkspaceInvitationLinkHandler:
    """Тесты GenerateWorkspaceInvitationLinkHandler."""

    @pytest.fixture
    def handler(self, ws_invitation_repo) -> GenerateWorkspaceInvitationLinkHandler:
        return GenerateWorkspaceInvitationLinkHandler(
            invitation_repo=ws_invitation_repo,
            permission_checker=_AlwaysAllowPermissionChecker(),
            event_bus=_NoopEventBus(),
        )

    async def test_generate_link_success(self, handler, ws_invitation_repo, make_workspace) -> None:
        ws = await make_workspace()
        cmd = GenerateWorkspaceInvitationLinkCommand(
            caller_id=str(ws.owner_ids[0]),
            workspace_id=str(ws.id),
            role_id=str(Id.generate()),
            invited_by=str(ws.owner_ids[0]),
        )
        result = await handler.handle(cmd)

        assert result.link is not None
        assert result.link["value"] is not None
        assert result.status == "pending"
        assert result.workspace_id == str(ws.id)

    async def test_generate_link_with_max_uses(self, handler, make_workspace) -> None:
        ws = await make_workspace()
        cmd = GenerateWorkspaceInvitationLinkCommand(
            caller_id=str(ws.owner_ids[0]),
            workspace_id=str(ws.id),
            role_id=str(Id.generate()),
            invited_by=str(ws.owner_ids[0]),
            max_uses=10,
        )
        result = await handler.handle(cmd)

        assert result.link is not None
        assert result.link["max_uses"] == 10

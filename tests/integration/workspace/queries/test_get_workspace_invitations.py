"""Интеграционные тесты GetWorkspaceInvitationsHandler."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.queries.get_workspace_invitations import (
    GetWorkspaceInvitationsQuery,
    GetWorkspaceInvitationsHandler,
)


@pytest.mark.integration
class TestGetWorkspaceInvitationsHandler:
    """Тесты GetWorkspaceInvitationsHandler."""

    @pytest.fixture
    def handler(self, ws_invitation_repo, ws_repo, permission_checker_stub) -> GetWorkspaceInvitationsHandler:
        return GetWorkspaceInvitationsHandler(
            invitation_repo=ws_invitation_repo,
            ws_repo=ws_repo,
            permission_checker=permission_checker_stub,
        )

    async def test_get_invitations_found(self, handler, make_workspace_invitation) -> None:
        inv = await make_workspace_invitation()
        query = GetWorkspaceInvitationsQuery(
            caller_id=str(Id.generate()), workspace_id=str(inv.workspace_id),
        )
        result = await handler.handle(query)

        assert result.total >= 1

    async def test_get_invitations_empty(self, handler, make_workspace) -> None:
        ws = await make_workspace()
        query = GetWorkspaceInvitationsQuery(
            caller_id=str(Id.generate()), workspace_id=str(ws.id),
        )
        result = await handler.handle(query)

        assert result.total == 0

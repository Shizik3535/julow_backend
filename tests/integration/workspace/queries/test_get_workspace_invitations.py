"""Интеграционные тесты GetWorkspaceInvitationsHandler."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.queries.get_workspace_invitations import (
    GetWorkspaceInvitationsQuery,
    GetWorkspaceInvitationsHandler,
)
from tests.integration.workspace.conftest import _AlwaysAllowPermissionChecker


@pytest.mark.integration
class TestGetWorkspaceInvitationsHandler:
    """Тесты GetWorkspaceInvitationsHandler."""

    @pytest.fixture
    def handler(self, ws_invitation_repo) -> GetWorkspaceInvitationsHandler:
        return GetWorkspaceInvitationsHandler(
            invitation_repo=ws_invitation_repo,
            permission_checker=_AlwaysAllowPermissionChecker(),
        )

    async def test_get_invitations_found(self, handler, make_workspace_invitation) -> None:
        inv = await make_workspace_invitation()
        query = GetWorkspaceInvitationsQuery(
            caller_id=str(Id.generate()), workspace_id=str(inv.workspace_id),
        )
        result = await handler.handle(query)

        assert result.total >= 1

    async def test_get_invitations_empty(self, handler) -> None:
        query = GetWorkspaceInvitationsQuery(
            caller_id=str(Id.generate()), workspace_id=str(Id.generate()),
        )
        result = await handler.handle(query)

        assert result.total == 0

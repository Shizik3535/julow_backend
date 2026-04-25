"""Интеграционные тесты GetWorkspaceInvitationByTokenHandler."""

import pytest

from app.context.workspace.application.queries.get_workspace_invitation_by_token import (
    GetWorkspaceInvitationByTokenQuery,
    GetWorkspaceInvitationByTokenHandler,
)
from app.context.workspace.domain.exceptions.workspace_invitation_exceptions import InvitationNotFoundException


@pytest.mark.integration
class TestGetWorkspaceInvitationByTokenHandler:
    """Тесты GetWorkspaceInvitationByTokenHandler."""

    @pytest.fixture
    def handler(self, ws_invitation_repo) -> GetWorkspaceInvitationByTokenHandler:
        return GetWorkspaceInvitationByTokenHandler(invitation_repo=ws_invitation_repo)

    async def test_get_by_token_found(self, handler, make_link_invitation) -> None:
        inv = await make_link_invitation(token_value="find-this-token")
        query = GetWorkspaceInvitationByTokenQuery(token="find-this-token")
        result = await handler.handle(query)

        assert result.id == str(inv.id)
        assert result.link is not None
        assert result.link["value"] == "find-this-token"

    async def test_get_by_token_not_found(self, handler) -> None:
        query = GetWorkspaceInvitationByTokenQuery(token="nonexistent-token")
        with pytest.raises(InvitationNotFoundException):
            await handler.handle(query)

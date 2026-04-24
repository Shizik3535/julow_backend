"""Интеграционные тесты GetInvitationByTokenHandler (реальные repos)."""

import pytest

from app.context.organization.application.dto.invitation_dto import InvitationDTO
from app.context.organization.application.queries.get_invitation_by_token import (
    GetInvitationByTokenHandler,
    GetInvitationByTokenQuery,
)
from app.context.organization.domain.exceptions.invitation_exceptions import InvitationNotFoundException


@pytest.mark.integration
class TestGetInvitationByTokenHandler:
    @pytest.fixture
    def handler(self, invitation_repo) -> GetInvitationByTokenHandler:
        return GetInvitationByTokenHandler(invitation_repo=invitation_repo)

    async def test_returns_invitation_dto(self, handler, make_link_invitation) -> None:
        inv = await make_link_invitation(token_value="find-me-123")
        query = GetInvitationByTokenQuery(token="find-me-123")
        result = await handler.handle(query)
        assert isinstance(result, InvitationDTO)
        assert result.link is not None
        assert result.link["value"] == "find-me-123"

    async def test_not_found_raises(self, handler) -> None:
        query = GetInvitationByTokenQuery(token="nonexistent-token")
        with pytest.raises(InvitationNotFoundException):
            await handler.handle(query)

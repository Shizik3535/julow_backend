"""Интеграционные тесты GetInvitationsByOrgHandler (реальные repos)."""

import pytest

from app.context.organization.application.dto.invitation_dto import InvitationListDTO
from app.context.organization.application.queries.get_invitations_by_org import (
    GetInvitationsByOrgHandler,
    GetInvitationsByOrgQuery,
)


@pytest.mark.integration
class TestGetInvitationsByOrgHandler:
    @pytest.fixture
    def handler(self, invitation_repo) -> GetInvitationsByOrgHandler:
        return GetInvitationsByOrgHandler(invitation_repo=invitation_repo)

    async def test_returns_invitations(self, handler, make_invitation, make_org) -> None:
        org = await make_org()
        inv = await make_invitation(org_id=org.id)
        query = GetInvitationsByOrgQuery(org_id=str(org.id))
        result = await handler.handle(query)
        assert isinstance(result, InvitationListDTO)
        assert any(i.id == str(inv.id) for i in result.items)

    async def test_empty_for_unknown_org(self, handler) -> None:
        from app.shared.domain.value_objects.id_vo import Id

        query = GetInvitationsByOrgQuery(org_id=str(Id.generate()))
        result = await handler.handle(query)
        assert result.total == 0

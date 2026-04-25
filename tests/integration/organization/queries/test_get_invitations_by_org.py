"""Интеграционные тесты GetInvitationsByOrgHandler (реальные repos)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.dto.invitation_dto import InvitationListDTO
from app.context.organization.application.queries.get_invitations_by_org import (
    GetInvitationsByOrgHandler,
    GetInvitationsByOrgQuery,
)


@pytest.mark.integration
class TestGetInvitationsByOrgHandler:
    @pytest.fixture
    def handler(self, invitation_repo, org_repo, permission_checker_stub) -> GetInvitationsByOrgHandler:
        return GetInvitationsByOrgHandler(invitation_repo=invitation_repo, org_repo=org_repo, org_permission_checker=permission_checker_stub)

    async def test_returns_invitations(self, handler, make_invitation, make_org) -> None:
        org = await make_org()
        inv = await make_invitation(org_id=org.id)
        query = GetInvitationsByOrgQuery(caller_id=str(Id.generate()), org_id=str(org.id))
        result = await handler.handle(query)
        assert isinstance(result, InvitationListDTO)
        assert any(i.id == str(inv.id) for i in result.items)

    async def test_not_found_raises_for_unknown_org(self, handler) -> None:
        from app.context.organization.domain.exceptions.organization_exceptions import OrganizationNotFoundException

        query = GetInvitationsByOrgQuery(caller_id=str(Id.generate()), org_id=str(Id.generate()))
        with pytest.raises(OrganizationNotFoundException):
            await handler.handle(query)

"""Интеграционные тесты GenerateInvitationLinkHandler (реальные repos + stubs)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.commands.generate_invitation_link import (
    GenerateInvitationLinkCommand,
    GenerateInvitationLinkHandler,
)
from app.context.organization.application.dto.invitation_dto import InvitationDTO


@pytest.mark.integration
class TestGenerateInvitationLinkHandler:
    @pytest.fixture
    def handler(self, org_repo, invitation_repo, permission_checker_stub, event_bus_stub):
        return GenerateInvitationLinkHandler(
            org_repo=org_repo,
            invitation_repo=invitation_repo,
            org_permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_generate_link(self, handler, make_org_with_membership) -> None:
        data = await make_org_with_membership()
        cmd = GenerateInvitationLinkCommand(
            caller_id=str(Id.generate()),
            org_id=str(data["org"].id),
            role_id=str(data["owner_role"].id),
            invited_by=str(data["owner_id"]),
        )
        result = await handler.handle(cmd)
        assert isinstance(result, InvitationDTO)
        assert result.link is not None
        assert result.link["value"] is not None

    async def test_generate_with_max_uses(self, handler, make_org_with_membership) -> None:
        data = await make_org_with_membership()
        cmd = GenerateInvitationLinkCommand(
            caller_id=str(Id.generate()),
            org_id=str(data["org"].id),
            role_id=str(data["owner_role"].id),
            invited_by=str(data["owner_id"]),
            max_uses=5,
        )
        result = await handler.handle(cmd)
        assert result.link["max_uses"] == 5

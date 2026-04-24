"""Интеграционные тесты SendInvitationHandler (реальные repos + stubs)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.commands.send_invitation import (
    SendInvitationCommand,
    SendInvitationHandler,
)
from app.context.organization.application.dto.invitation_dto import InvitationDTO
from app.context.organization.application.exceptions.invitation_app_exceptions import DuplicateInvitationForEmailException


@pytest.mark.integration
class TestSendInvitationHandler:
    @pytest.fixture
    def handler(self, org_repo, invitation_repo, permission_checker_stub, event_bus_stub):
        return SendInvitationHandler(
            org_repo=org_repo,
            invitation_repo=invitation_repo,
            org_permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_send_invitation(self, handler, make_org_with_membership) -> None:
        data = await make_org_with_membership()
        cmd = SendInvitationCommand(
            caller_id=str(Id.generate()),
            org_id=str(data["org"].id),
            email="new@example.com",
            role_id=str(data["owner_role"].id),
            invited_by=str(data["owner_id"]),
        )
        result = await handler.handle(cmd)
        assert isinstance(result, InvitationDTO)
        assert result.email == "new@example.com"

    async def test_duplicate_email_raises(self, handler, make_org_with_membership) -> None:
        data = await make_org_with_membership()
        cmd = SendInvitationCommand(
            caller_id=str(Id.generate()),
            org_id=str(data["org"].id),
            email="dup@example.com",
            role_id=str(data["owner_role"].id),
            invited_by=str(data["owner_id"]),
        )
        await handler.handle(cmd)
        with pytest.raises(DuplicateInvitationForEmailException):
            await handler.handle(cmd)

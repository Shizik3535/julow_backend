"""Интеграционные тесты SendBulkInvitationsHandler (реальные repos + stubs)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.commands.send_bulk_invitations import (
    SendBulkInvitationsCommand,
    SendBulkInvitationsHandler,
)
from app.context.organization.application.dto.invitation_dto import InvitationListDTO


@pytest.mark.integration
class TestSendBulkInvitationsHandler:
    @pytest.fixture
    def handler(self, org_repo, invitation_repo, permission_checker_stub, event_bus_stub):
        return SendBulkInvitationsHandler(
            org_repo=org_repo,
            invitation_repo=invitation_repo,
            org_permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_bulk_send(self, handler, make_org_with_membership) -> None:
        data = await make_org_with_membership()
        cmd = SendBulkInvitationsCommand(
            caller_id=str(Id.generate()),
            org_id=str(data["org"].id),
            emails=["a@test.com", "b@test.com"],
            role_id=str(data["owner_role"].id),
            invited_by=str(data["owner_id"]),
        )
        result = await handler.handle(cmd)
        assert isinstance(result, InvitationListDTO)
        assert result.total == 2

    async def test_skips_duplicate_emails(self, handler, make_org_with_membership) -> None:
        data = await make_org_with_membership()
        cmd1 = SendBulkInvitationsCommand(
            caller_id=str(Id.generate()),
            org_id=str(data["org"].id),
            emails=["dup@test.com"],
            role_id=str(data["owner_role"].id),
            invited_by=str(data["owner_id"]),
        )
        await handler.handle(cmd1)

        cmd2 = SendBulkInvitationsCommand(
            caller_id=str(Id.generate()),
            org_id=str(data["org"].id),
            emails=["dup@test.com", "new@test.com"],
            role_id=str(data["owner_role"].id),
            invited_by=str(data["owner_id"]),
        )
        result = await handler.handle(cmd2)
        assert result.total == 1

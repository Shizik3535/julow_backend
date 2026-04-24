"""Интеграционные тесты AcceptInvitationHandler (реальные repos + stubs)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.commands.accept_invitation import (
    AcceptInvitationCommand,
    AcceptInvitationHandler,
)
from app.context.organization.domain.value_objects.invitation_status import InvitationStatus


@pytest.mark.integration
class TestAcceptInvitationHandler:
    @pytest.fixture
    def handler(self, invitation_repo, membership_repo, identity_user_stub, event_bus_stub):
        return AcceptInvitationHandler(
            invitation_repo=invitation_repo,
            membership_repo=membership_repo,
            identity_port=identity_user_stub,
            event_bus=event_bus_stub,
        )

    async def test_accept_email_invitation(
        self, handler, make_org_with_membership, make_invitation, invitation_repo, membership_repo
    ) -> None:
        data = await make_org_with_membership()
        inv = await make_invitation(org_id=data["org"].id, role_id=data["owner_role"].id)
        accepting_user = Id.generate()

        cmd = AcceptInvitationCommand(
            invitation_id=str(inv.id),
            user_id=str(accepting_user),
        )
        await handler.handle(cmd)

        found_inv = await invitation_repo.get_by_id(inv.id)
        assert found_inv is not None
        assert found_inv.status == InvitationStatus.ACCEPTED

        membership = await membership_repo.get_by_org_id(data["org"].id)
        assert membership is not None
        assert any(m.user_id == accepting_user for m in membership.members)

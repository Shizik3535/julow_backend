"""Интеграционные тесты AcceptWorkspaceInvitationHandler."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.commands.accept_workspace_invitation import (
    AcceptWorkspaceInvitationCommand,
    AcceptWorkspaceInvitationHandler,
)
from app.context.workspace.application.exceptions.membership_app_exceptions import (
    MemberAlreadyExistsException,
    UserNotFoundException,
)
from app.context.workspace.application.exceptions.invitation_app_exceptions import (
    DuplicateInvitationForEmailException,
    InvitationAlreadyProcessedException,
)
from app.context.workspace.domain.exceptions.workspace_invitation_exceptions import InvitationNotFoundException
from app.context.workspace.domain.value_objects.invitation_status import InvitationStatus
from app.context.workspace.domain.value_objects.member_source import MemberSource
from tests.integration.workspace.conftest import _StubIdentityUserPort, _NoopEventBus


@pytest.mark.integration
class TestAcceptWorkspaceInvitationHandler:
    """Тесты AcceptWorkspaceInvitationHandler."""

    @pytest.fixture
    def handler(self, ws_invitation_repo, ws_membership_repo) -> AcceptWorkspaceInvitationHandler:
        return AcceptWorkspaceInvitationHandler(
            invitation_repo=ws_invitation_repo,
            membership_repo=ws_membership_repo,
            identity_port=_StubIdentityUserPort(),
            event_bus=_NoopEventBus(),
        )

    async def test_accept_email_invitation_success(
        self, handler, ws_invitation_repo, ws_membership_repo, make_workspace_with_membership,
        make_workspace_invitation
    ) -> None:
        data = await make_workspace_with_membership()
        ws = data["workspace"]
        inv = await make_workspace_invitation(
            workspace_id=ws.id,
            role_id=Id.generate(),
            invited_by=ws.owner_ids[0],
        )

        accepting_user = Id.generate()
        cmd = AcceptWorkspaceInvitationCommand(
            invitation_id=str(inv.id),
            user_id=str(accepting_user),
        )
        await handler.handle(cmd)

        found_inv = await ws_invitation_repo.get_by_id(inv.id)
        assert found_inv is not None
        assert found_inv.status == InvitationStatus.ACCEPTED

        membership = await ws_membership_repo.get_by_workspace_id(ws.id)
        assert membership is not None
        member = membership._find_member(accepting_user)
        assert member is not None
        assert member.source == MemberSource.DIRECT

    async def test_accept_link_invitation(
        self, handler, ws_invitation_repo, ws_membership_repo, make_workspace_with_membership,
        make_link_invitation
    ) -> None:
        data = await make_workspace_with_membership()
        ws = data["workspace"]
        inv = await make_link_invitation(
            workspace_id=ws.id,
            role_id=Id.generate(),
            invited_by=ws.owner_ids[0],
        )

        accepting_user = Id.generate()
        cmd = AcceptWorkspaceInvitationCommand(
            invitation_id=str(inv.id),
            user_id=str(accepting_user),
        )
        await handler.handle(cmd)

        membership = await ws_membership_repo.get_by_workspace_id(ws.id)
        assert membership is not None
        member = membership._find_member(accepting_user)
        assert member is not None
        assert member.source == MemberSource.INVITATION_LINK

    async def test_accept_invitation_user_not_found(self, ws_invitation_repo, ws_membership_repo) -> None:
        class _NoUserPort(_StubIdentityUserPort):
            async def user_exists(self, user_id: str) -> bool:
                return False

        handler = AcceptWorkspaceInvitationHandler(
            invitation_repo=ws_invitation_repo,
            membership_repo=ws_membership_repo,
            identity_port=_NoUserPort(),
            event_bus=_NoopEventBus(),
        )
        cmd = AcceptWorkspaceInvitationCommand(
            invitation_id=str(Id.generate()),
            user_id=str(Id.generate()),
        )
        with pytest.raises(UserNotFoundException):
            await handler.handle(cmd)

    async def test_accept_invitation_not_found(self, handler) -> None:
        cmd = AcceptWorkspaceInvitationCommand(
            invitation_id=str(Id.generate()),
            user_id=str(Id.generate()),
        )
        with pytest.raises(InvitationNotFoundException):
            await handler.handle(cmd)

    async def test_accept_already_member(
        self, handler, ws_invitation_repo, ws_membership_repo, make_workspace_with_membership,
        make_workspace_invitation
    ) -> None:
        data = await make_workspace_with_membership()
        ws = data["workspace"]
        owner_id = data["owner_id"]
        inv = await make_workspace_invitation(
            workspace_id=ws.id,
            role_id=Id.generate(),
            invited_by=ws.owner_ids[0],
        )

        cmd = AcceptWorkspaceInvitationCommand(
            invitation_id=str(inv.id),
            user_id=str(owner_id),
        )
        with pytest.raises(MemberAlreadyExistsException):
            await handler.handle(cmd)

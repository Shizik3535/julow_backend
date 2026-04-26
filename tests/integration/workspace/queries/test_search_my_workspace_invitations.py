"""Интеграционные тесты SearchMyWorkspaceInvitationsHandler."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.queries.search_my_workspace_invitations import (
    SearchMyWorkspaceInvitationsHandler,
    SearchMyWorkspaceInvitationsQuery,
)
from app.context.workspace.application.ports.integration.inboard.identity_user_port import IdentityUserPort
from app.context.workspace.domain.value_objects.invitation_status import InvitationStatus
from tests.integration.workspace.conftest import _NoopEventBus


class _FixedEmailIdentityUserPort(IdentityUserPort):
    """Stub: возвращает заданный email для любого user_id."""

    def __init__(self, email: str = "my-ws@example.com") -> None:
        self._email = email

    async def user_exists(self, user_id: str) -> bool:
        return True

    async def get_user(self, user_id: str) -> dict | None:
        return {"id": user_id, "email": self._email}


@pytest.mark.integration
class TestSearchMyWorkspaceInvitationsHandler:
    @pytest.fixture
    def handler(self, ws_invitation_repo) -> SearchMyWorkspaceInvitationsHandler:
        return SearchMyWorkspaceInvitationsHandler(
            invitation_repo=ws_invitation_repo,
            identity_port=_FixedEmailIdentityUserPort(email="my-ws@example.com"),
        )

    async def test_search_my_pending_invitations(
        self, handler, make_workspace_invitation, make_workspace
    ) -> None:
        ws = await make_workspace()
        inv = await make_workspace_invitation(workspace_id=ws.id, email="my-ws@example.com")
        query = SearchMyWorkspaceInvitationsQuery(caller_id=str(Id.generate()))
        dto = await handler.handle(query)

        assert dto.total >= 1
        assert any(i.id == str(inv.id) for i in dto.items)

    async def test_search_my_accepted_invitations(
        self, ws_invitation_repo, make_workspace_invitation, make_workspace
    ) -> None:
        ws = await make_workspace()
        inv = await make_workspace_invitation(workspace_id=ws.id, email="my-ws@example.com")
        accepting_user = Id.generate()
        inv.accept(user_id=accepting_user)
        inv.clear_domain_events()
        await ws_invitation_repo.update(inv)

        handler = SearchMyWorkspaceInvitationsHandler(
            invitation_repo=ws_invitation_repo,
            identity_port=_FixedEmailIdentityUserPort(email="other-ws@example.com"),
        )
        query = SearchMyWorkspaceInvitationsQuery(caller_id=str(accepting_user))
        dto = await handler.handle(query)

        assert dto.total >= 1
        assert any(i.id == str(inv.id) for i in dto.items)

    async def test_search_my_invitations_empty(
        self, handler
    ) -> None:
        query = SearchMyWorkspaceInvitationsQuery(caller_id=str(Id.generate()))
        dto = await handler.handle(query)
        assert dto.total == 0
        assert len(dto.items) == 0

    async def test_search_my_invitations_user_not_found(
        self, ws_invitation_repo
    ) -> None:
        class _NoUserPort(IdentityUserPort):
            async def user_exists(self, user_id: str) -> bool:
                return False

            async def get_user(self, user_id: str) -> dict | None:
                return None

        handler = SearchMyWorkspaceInvitationsHandler(
            invitation_repo=ws_invitation_repo,
            identity_port=_NoUserPort(),
        )
        query = SearchMyWorkspaceInvitationsQuery(caller_id=str(Id.generate()))
        dto = await handler.handle(query)
        assert dto.total == 0
        assert len(dto.items) == 0

    async def test_search_my_invitations_with_status_filter(
        self, handler, make_workspace_invitation, make_workspace
    ) -> None:
        ws = await make_workspace()
        await make_workspace_invitation(workspace_id=ws.id, email="my-ws@example.com")
        query = SearchMyWorkspaceInvitationsQuery(
            caller_id=str(Id.generate()),
            filters={"status": "pending"},
        )
        dto = await handler.handle(query)
        assert all(i.status == "pending" for i in dto.items)

    async def test_search_my_invitations_pagination(
        self, handler, make_workspace_invitation, make_workspace
    ) -> None:
        ws = await make_workspace()
        for i in range(5):
            await make_workspace_invitation(workspace_id=ws.id, email="my-ws@example.com")
        query = SearchMyWorkspaceInvitationsQuery(
            caller_id=str(Id.generate()),
            offset=0,
            limit=2,
        )
        dto = await handler.handle(query)
        assert dto.total >= 5
        assert len(dto.items) == 2

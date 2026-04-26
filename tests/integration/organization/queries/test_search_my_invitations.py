"""Интеграционные тесты SearchMyInvitationsHandler."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.queries.search_my_invitations import (
    SearchMyInvitationsHandler,
    SearchMyInvitationsQuery,
)
from app.context.organization.application.ports.integration.inboard.identity_user_port import IdentityUserPort
from app.context.organization.domain.value_objects.invitation_status import InvitationStatus
from tests.integration.organization.conftest import _NoopEventBus


class _FixedEmailIdentityUserPort(IdentityUserPort):
    """Stub: возвращает заданный email для любого user_id."""

    def __init__(self, email: str = "my@example.com") -> None:
        self._email = email

    async def user_exists(self, user_id: str) -> bool:
        return True

    async def get_user(self, user_id: str) -> dict | None:
        return {"id": user_id, "email": self._email}


@pytest.mark.integration
class TestSearchMyInvitationsHandler:
    @pytest.fixture
    def handler(self, invitation_repo) -> SearchMyInvitationsHandler:
        return SearchMyInvitationsHandler(
            invitation_repo=invitation_repo,
            identity_port=_FixedEmailIdentityUserPort(email="my@example.com"),
        )

    async def test_search_my_pending_invitations(
        self, handler, make_invitation, make_org
    ) -> None:
        org = await make_org()
        inv = await make_invitation(org_id=org.id, email="my@example.com")
        query = SearchMyInvitationsQuery(caller_id=str(Id.generate()))
        dto = await handler.handle(query)

        assert dto.total >= 1
        assert any(i.id == str(inv.id) for i in dto.items)

    async def test_search_my_accepted_invitations(
        self, invitation_repo, make_invitation, make_org
    ) -> None:
        org = await make_org()
        inv = await make_invitation(org_id=org.id, email="my@example.com")
        accepting_user = Id.generate()
        inv.accept(user_id=accepting_user)
        inv.clear_domain_events()
        await invitation_repo.update(inv)

        handler = SearchMyInvitationsHandler(
            invitation_repo=invitation_repo,
            identity_port=_FixedEmailIdentityUserPort(email="other@example.com"),
        )
        query = SearchMyInvitationsQuery(caller_id=str(accepting_user))
        dto = await handler.handle(query)

        assert dto.total >= 1
        assert any(i.id == str(inv.id) for i in dto.items)

    async def test_search_my_invitations_empty(
        self, handler
    ) -> None:
        query = SearchMyInvitationsQuery(caller_id=str(Id.generate()))
        dto = await handler.handle(query)
        assert dto.total == 0
        assert len(dto.items) == 0

    async def test_search_my_invitations_user_not_found(
        self, invitation_repo
    ) -> None:
        class _NoUserPort(IdentityUserPort):
            async def user_exists(self, user_id: str) -> bool:
                return False

            async def get_user(self, user_id: str) -> dict | None:
                return None

        handler = SearchMyInvitationsHandler(
            invitation_repo=invitation_repo,
            identity_port=_NoUserPort(),
        )
        query = SearchMyInvitationsQuery(caller_id=str(Id.generate()))
        dto = await handler.handle(query)
        assert dto.total == 0
        assert len(dto.items) == 0

    async def test_search_my_invitations_with_status_filter(
        self, handler, make_invitation, make_org
    ) -> None:
        org = await make_org()
        await make_invitation(org_id=org.id, email="my@example.com")
        query = SearchMyInvitationsQuery(
            caller_id=str(Id.generate()),
            filters={"status": "pending"},
        )
        dto = await handler.handle(query)
        assert all(i.status == "pending" for i in dto.items)

    async def test_search_my_invitations_pagination(
        self, handler, make_invitation, make_org
    ) -> None:
        org = await make_org()
        for i in range(5):
            await make_invitation(org_id=org.id, email="my@example.com")
        query = SearchMyInvitationsQuery(
            caller_id=str(Id.generate()),
            offset=0,
            limit=2,
        )
        dto = await handler.handle(query)
        assert dto.total >= 5
        assert len(dto.items) == 2

"""Интеграционные тесты SqlWorkspaceInvitationRepository (реальная PostgreSQL)."""

import pytest

from app.shared.domain.value_objects.email_vo import Email
from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.domain.aggregates.workspace_invitation import WorkspaceInvitation
from app.context.workspace.domain.value_objects.invitation_status import InvitationStatus
from app.context.workspace.infrastructure.persistence.repositories.sql_workspace_invitation_repository import (
    SqlWorkspaceInvitationRepository,
)


@pytest.mark.integration
class TestSqlWorkspaceInvitationRepositoryAdd:
    """Тесты добавления WorkspaceInvitation."""

    async def test_add_email_invitation_and_get_by_id(
        self, ws_invitation_repo: SqlWorkspaceInvitationRepository, make_workspace
    ) -> None:
        ws = await make_workspace()
        inv = WorkspaceInvitation.create_email_invitation(
            workspace_id=ws.id,
            email=Email("test@example.com"),
            role_id=Id.generate(),
            invited_by=ws.owner_ids[0],
        )
        inv.clear_domain_events()
        await ws_invitation_repo.add(inv)

        found = await ws_invitation_repo.get_by_id(inv.id)
        assert found is not None
        assert found.id == inv.id

    async def test_add_link_invitation_and_get_by_id(
        self, ws_invitation_repo: SqlWorkspaceInvitationRepository, make_workspace
    ) -> None:
        ws = await make_workspace()
        inv = WorkspaceInvitation.create_link_invitation(
            workspace_id=ws.id,
            role_id=Id.generate(),
            invited_by=ws.owner_ids[0],
            token_value="test-token-123",
        )
        inv.clear_domain_events()
        await ws_invitation_repo.add(inv)

        found = await ws_invitation_repo.get_by_id(inv.id)
        assert found is not None
        assert found.link is not None
        assert found.link.value == "test-token-123"

    async def test_add_persists_attributes(
        self, ws_invitation_repo: SqlWorkspaceInvitationRepository, make_workspace
    ) -> None:
        ws = await make_workspace()
        role_id = Id.generate()
        inv = WorkspaceInvitation.create_email_invitation(
            workspace_id=ws.id,
            email=Email("attrs@example.com"),
            role_id=role_id,
            invited_by=ws.owner_ids[0],
        )
        inv.clear_domain_events()
        await ws_invitation_repo.add(inv)

        found = await ws_invitation_repo.get_by_id(inv.id)
        assert found is not None
        assert found.workspace_id == ws.id
        assert str(found.email) == "attrs@example.com"
        assert found.role_id == role_id
        assert found.status == InvitationStatus.PENDING


@pytest.mark.integration
class TestSqlWorkspaceInvitationRepositorySearch:
    """Тесты поиска WorkspaceInvitation."""

    async def test_get_by_workspace_id(
        self, ws_invitation_repo: SqlWorkspaceInvitationRepository, make_workspace
    ) -> None:
        ws = await make_workspace()
        inv = WorkspaceInvitation.create_email_invitation(
            workspace_id=ws.id,
            email=Email("ws-search@example.com"),
            role_id=Id.generate(),
            invited_by=ws.owner_ids[0],
        )
        inv.clear_domain_events()
        await ws_invitation_repo.add(inv)

        result = await ws_invitation_repo.get_by_workspace_id(ws.id)
        assert len(result) >= 1

    async def test_get_by_token(
        self, ws_invitation_repo: SqlWorkspaceInvitationRepository, make_workspace
    ) -> None:
        ws = await make_workspace()
        inv = WorkspaceInvitation.create_link_invitation(
            workspace_id=ws.id,
            role_id=Id.generate(),
            invited_by=ws.owner_ids[0],
            token_value="unique-token-xyz",
        )
        inv.clear_domain_events()
        await ws_invitation_repo.add(inv)

        found = await ws_invitation_repo.get_by_token("unique-token-xyz")
        assert found is not None
        assert found.id == inv.id

    async def test_get_by_token_not_found(self, ws_invitation_repo: SqlWorkspaceInvitationRepository) -> None:
        found = await ws_invitation_repo.get_by_token("nonexistent-token")
        assert found is None

    async def test_get_pending_by_workspace(
        self, ws_invitation_repo: SqlWorkspaceInvitationRepository, make_workspace
    ) -> None:
        ws = await make_workspace()
        inv = WorkspaceInvitation.create_email_invitation(
            workspace_id=ws.id,
            email=Email("pending@example.com"),
            role_id=Id.generate(),
            invited_by=ws.owner_ids[0],
        )
        inv.clear_domain_events()
        await ws_invitation_repo.add(inv)

        result = await ws_invitation_repo.get_pending_by_workspace(ws.id)
        assert len(result) >= 1
        assert all(i.status == InvitationStatus.PENDING for i in result)


@pytest.mark.integration
class TestSqlWorkspaceInvitationRepositoryUpdate:
    """Тесты обновления WorkspaceInvitation."""

    async def test_accept_invitation(
        self, ws_invitation_repo: SqlWorkspaceInvitationRepository, make_workspace
    ) -> None:
        ws = await make_workspace()
        inv = WorkspaceInvitation.create_email_invitation(
            workspace_id=ws.id,
            email=Email("accept@example.com"),
            role_id=Id.generate(),
            invited_by=ws.owner_ids[0],
        )
        inv.clear_domain_events()
        await ws_invitation_repo.add(inv)

        accepting_user = Id.generate()
        inv.accept(user_id=accepting_user)
        inv.clear_domain_events()
        await ws_invitation_repo.update(inv)

        found = await ws_invitation_repo.get_by_id(inv.id)
        assert found is not None
        assert found.status == InvitationStatus.ACCEPTED
        assert found.user_id == accepting_user

    async def test_decline_invitation(
        self, ws_invitation_repo: SqlWorkspaceInvitationRepository, make_workspace
    ) -> None:
        ws = await make_workspace()
        inv = WorkspaceInvitation.create_email_invitation(
            workspace_id=ws.id,
            email=Email("decline@example.com"),
            role_id=Id.generate(),
            invited_by=ws.owner_ids[0],
        )
        inv.clear_domain_events()
        await ws_invitation_repo.add(inv)

        declining_user = Id.generate()
        inv.decline(user_id=declining_user)
        inv.clear_domain_events()
        await ws_invitation_repo.update(inv)

        found = await ws_invitation_repo.get_by_id(inv.id)
        assert found is not None
        assert found.status == InvitationStatus.DECLINED
        assert found.user_id == declining_user

    async def test_revoke_invitation(
        self, ws_invitation_repo: SqlWorkspaceInvitationRepository, make_workspace
    ) -> None:
        ws = await make_workspace()
        inv = WorkspaceInvitation.create_email_invitation(
            workspace_id=ws.id,
            email=Email("revoke@example.com"),
            role_id=Id.generate(),
            invited_by=ws.owner_ids[0],
        )
        inv.clear_domain_events()
        await ws_invitation_repo.add(inv)

        inv.revoke()
        inv.clear_domain_events()
        await ws_invitation_repo.update(inv)

        found = await ws_invitation_repo.get_by_id(inv.id)
        assert found is not None
        assert found.status == InvitationStatus.REVOKED


@pytest.mark.integration
class TestSqlWorkspaceInvitationRepositorySearchByUser:
    """Тесты search_by_user."""

    async def test_search_by_user_email_pending(
        self, ws_invitation_repo: SqlWorkspaceInvitationRepository, make_workspace_invitation, make_workspace
    ) -> None:
        ws = await make_workspace()
        inv = await make_workspace_invitation(workspace_id=ws.id, email="findme-ws@example.com")
        results, total = await ws_invitation_repo.search_by_user(email="findme-ws@example.com")
        assert total >= 1
        assert any(i.id == inv.id for i in results)

    async def test_search_by_user_email_not_found_other_email(
        self, ws_invitation_repo: SqlWorkspaceInvitationRepository, make_workspace_invitation, make_workspace
    ) -> None:
        ws = await make_workspace()
        await make_workspace_invitation(workspace_id=ws.id, email="other-ws@example.com")
        results, total = await ws_invitation_repo.search_by_user(email="notexist-ws@example.com")
        assert total == 0
        assert len(results) == 0

    async def test_search_by_user_id_accepted(
        self, ws_invitation_repo: SqlWorkspaceInvitationRepository, make_workspace_invitation, make_workspace
    ) -> None:
        ws = await make_workspace()
        inv = await make_workspace_invitation(workspace_id=ws.id, email="accept-ws@example.com")
        accepting_user = Id.generate()
        inv.accept(user_id=accepting_user)
        inv.clear_domain_events()
        await ws_invitation_repo.update(inv)

        results, total = await ws_invitation_repo.search_by_user(
            email="nomatch-ws@example.com", user_id=accepting_user,
        )
        assert total >= 1
        assert any(i.id == inv.id for i in results)

    async def test_search_by_user_pagination(
        self, ws_invitation_repo: SqlWorkspaceInvitationRepository, make_workspace_invitation, make_workspace
    ) -> None:
        ws = await make_workspace()
        for i in range(5):
            await make_workspace_invitation(workspace_id=ws.id, email="page-ws@example.com")
        results, total = await ws_invitation_repo.search_by_user(
            email="page-ws@example.com", limit=2,
        )
        assert total >= 5
        assert len(results) == 2

    async def test_search_by_user_filter_by_workspace_id(
        self, ws_invitation_repo: SqlWorkspaceInvitationRepository, make_workspace_invitation, make_workspace
    ) -> None:
        ws1 = await make_workspace()
        ws2 = await make_workspace()
        inv1 = await make_workspace_invitation(workspace_id=ws1.id, email="filter-ws@example.com")
        await make_workspace_invitation(workspace_id=ws2.id, email="filter-ws@example.com")

        results, total = await ws_invitation_repo.search_by_user(
            email="filter-ws@example.com",
            filters={"workspace_id": str(ws1.id)},
        )
        assert total >= 1
        assert any(i.id == inv1.id for i in results)
        assert not any(i.workspace_id == ws2.id for i in results)

    async def test_search_by_user_filter_by_status(
        self, ws_invitation_repo: SqlWorkspaceInvitationRepository, make_workspace_invitation, make_workspace
    ) -> None:
        ws = await make_workspace()
        inv = await make_workspace_invitation(workspace_id=ws.id, email="status-ws@example.com")
        accepting_user = Id.generate()
        inv.accept(user_id=accepting_user)
        inv.clear_domain_events()
        await ws_invitation_repo.update(inv)

        results, total = await ws_invitation_repo.search_by_user(
            email="status-ws@example.com",
            user_id=accepting_user,
            filters={"status": "accepted"},
        )
        assert total >= 1
        assert all(i.status == InvitationStatus.ACCEPTED for i in results)

    async def test_search_by_user_total_count(
        self, ws_invitation_repo: SqlWorkspaceInvitationRepository, make_workspace_invitation, make_workspace
    ) -> None:
        ws = await make_workspace()
        for i in range(3):
            await make_workspace_invitation(workspace_id=ws.id, email="total-ws@example.com")
        _, total = await ws_invitation_repo.search_by_user(email="total-ws@example.com")
        assert total >= 3


@pytest.mark.integration
class TestSqlWorkspaceInvitationRepositoryDelete:
    """Тесты удаления WorkspaceInvitation."""

    async def test_delete(self, ws_invitation_repo: SqlWorkspaceInvitationRepository, make_workspace) -> None:
        ws = await make_workspace()
        inv = WorkspaceInvitation.create_email_invitation(
            workspace_id=ws.id,
            email=Email("delete@example.com"),
            role_id=Id.generate(),
            invited_by=ws.owner_ids[0],
        )
        inv.clear_domain_events()
        await ws_invitation_repo.add(inv)

        await ws_invitation_repo.delete(inv.id)
        found = await ws_invitation_repo.get_by_id(inv.id)
        assert found is None

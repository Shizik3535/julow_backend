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

        inv.accept(user_id=Id.generate())
        inv.clear_domain_events()
        await ws_invitation_repo.update(inv)

        found = await ws_invitation_repo.get_by_id(inv.id)
        assert found is not None
        assert found.status == InvitationStatus.ACCEPTED

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

        inv.decline()
        inv.clear_domain_events()
        await ws_invitation_repo.update(inv)

        found = await ws_invitation_repo.get_by_id(inv.id)
        assert found is not None
        assert found.status == InvitationStatus.DECLINED

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

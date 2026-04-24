"""Интеграционные тесты SqlInvitationRepository (реальная PostgreSQL)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.email_vo import Email
from app.context.organization.domain.aggregates.invitation import Invitation
from app.context.organization.domain.value_objects.invitation_status import InvitationStatus
from app.context.organization.infrastructure.persistence.repositories.sql_invitation_repository import (
    SqlInvitationRepository,
)


@pytest.mark.integration
class TestSqlInvitationRepositoryAdd:
    """Тесты добавления."""

    async def test_add_email_invitation_and_get(
        self, invitation_repo: SqlInvitationRepository, make_invitation
    ) -> None:
        inv = await make_invitation(email="test@example.com")
        found = await invitation_repo.get_by_id(inv.id)
        assert found is not None
        assert found.id == inv.id
        assert found.email is not None
        assert str(found.email) == "test@example.com"

    async def test_add_link_invitation_and_get(
        self, invitation_repo: SqlInvitationRepository, make_link_invitation
    ) -> None:
        inv = await make_link_invitation(token_value="my-token-123")
        found = await invitation_repo.get_by_id(inv.id)
        assert found is not None
        assert found.link is not None
        assert found.link.value == "my-token-123"


@pytest.mark.integration
class TestSqlInvitationRepositorySearch:
    """Тесты поиска."""

    async def test_get_by_org_id(
        self, invitation_repo: SqlInvitationRepository, make_invitation, make_org
    ) -> None:
        org = await make_org()
        inv = await make_invitation(org_id=org.id)
        found = await invitation_repo.get_by_org_id(org.id)
        assert len(found) >= 1
        assert any(i.id == inv.id for i in found)

    async def test_get_by_token_found(
        self, invitation_repo: SqlInvitationRepository, make_link_invitation
    ) -> None:
        inv = await make_link_invitation(token_value="findable-token")
        found = await invitation_repo.get_by_token("findable-token")
        assert found is not None
        assert found.id == inv.id

    async def test_get_by_token_not_found(self, invitation_repo: SqlInvitationRepository) -> None:
        found = await invitation_repo.get_by_token("nonexistent-token")
        assert found is None

    async def test_get_pending_by_org(
        self, invitation_repo: SqlInvitationRepository, make_invitation, make_org
    ) -> None:
        org = await make_org()
        inv = await make_invitation(org_id=org.id)
        found = await invitation_repo.get_pending_by_org(org.id)
        assert len(found) >= 1
        assert all(i.status == InvitationStatus.PENDING for i in found)


@pytest.mark.integration
class TestSqlInvitationRepositoryUpdate:
    """Тесты обновления."""

    async def test_update_accept(
        self, invitation_repo: SqlInvitationRepository, make_invitation
    ) -> None:
        inv = await make_invitation()
        inv.accept(user_id=Id.generate())
        inv.clear_domain_events()
        await invitation_repo.update(inv)

        found = await invitation_repo.get_by_id(inv.id)
        assert found is not None
        assert found.status == InvitationStatus.ACCEPTED

    async def test_update_decline(
        self, invitation_repo: SqlInvitationRepository, make_invitation
    ) -> None:
        inv = await make_invitation()
        inv.decline()
        inv.clear_domain_events()
        await invitation_repo.update(inv)

        found = await invitation_repo.get_by_id(inv.id)
        assert found is not None
        assert found.status == InvitationStatus.DECLINED

    async def test_update_revoke(
        self, invitation_repo: SqlInvitationRepository, make_invitation
    ) -> None:
        inv = await make_invitation()
        inv.revoke()
        inv.clear_domain_events()
        await invitation_repo.update(inv)

        found = await invitation_repo.get_by_id(inv.id)
        assert found is not None
        assert found.status == InvitationStatus.REVOKED

    async def test_update_increment_link_usage(
        self, invitation_repo: SqlInvitationRepository, make_link_invitation
    ) -> None:
        inv = await make_link_invitation()
        inv.increment_link_usage()
        inv.clear_domain_events()
        await invitation_repo.update(inv)

        found = await invitation_repo.get_by_id(inv.id)
        assert found is not None
        assert found.link is not None
        assert found.link.used_count == 1


@pytest.mark.integration
class TestSqlInvitationRepositoryDelete:
    """Тесты удаления."""

    async def test_delete(self, invitation_repo: SqlInvitationRepository, make_invitation) -> None:
        inv = await make_invitation()
        await invitation_repo.delete(inv.id)
        found = await invitation_repo.get_by_id(inv.id)
        assert found is None

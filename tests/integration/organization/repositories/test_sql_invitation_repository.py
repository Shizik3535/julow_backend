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
        accepting_user = Id.generate()
        inv.accept(user_id=accepting_user)
        inv.clear_domain_events()
        await invitation_repo.update(inv)

        found = await invitation_repo.get_by_id(inv.id)
        assert found is not None
        assert found.status == InvitationStatus.ACCEPTED
        assert found.user_id == accepting_user

    async def test_update_decline(
        self, invitation_repo: SqlInvitationRepository, make_invitation
    ) -> None:
        inv = await make_invitation()
        declining_user = Id.generate()
        inv.decline(user_id=declining_user)
        inv.clear_domain_events()
        await invitation_repo.update(inv)

        found = await invitation_repo.get_by_id(inv.id)
        assert found is not None
        assert found.status == InvitationStatus.DECLINED
        assert found.user_id == declining_user

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
class TestSqlInvitationRepositorySearchByUser:
    """Тесты search_by_user."""

    async def test_search_by_user_email_pending(
        self, invitation_repo: SqlInvitationRepository, make_invitation, make_org
    ) -> None:
        org = await make_org()
        inv = await make_invitation(org_id=org.id, email="findme@example.com")
        results, total = await invitation_repo.search_by_user(email="findme@example.com")
        assert total >= 1
        assert any(i.id == inv.id for i in results)

    async def test_search_by_user_email_not_found_other_email(
        self, invitation_repo: SqlInvitationRepository, make_invitation, make_org
    ) -> None:
        org = await make_org()
        await make_invitation(org_id=org.id, email="other@example.com")
        results, total = await invitation_repo.search_by_user(email="notexist@example.com")
        assert total == 0
        assert len(results) == 0

    async def test_search_by_user_id_accepted(
        self, invitation_repo: SqlInvitationRepository, make_invitation, make_org
    ) -> None:
        org = await make_org()
        inv = await make_invitation(org_id=org.id, email="accept@example.com")
        accepting_user = Id.generate()
        inv.accept(user_id=accepting_user)
        inv.clear_domain_events()
        await invitation_repo.update(inv)

        results, total = await invitation_repo.search_by_user(
            email="nomatch@example.com", user_id=accepting_user,
        )
        assert total >= 1
        assert any(i.id == inv.id for i in results)

    async def test_search_by_user_id_declined(
        self, invitation_repo: SqlInvitationRepository, make_invitation, make_org
    ) -> None:
        org = await make_org()
        inv = await make_invitation(org_id=org.id, email="decline@example.com")
        declining_user = Id.generate()
        inv.decline(user_id=declining_user)
        inv.clear_domain_events()
        await invitation_repo.update(inv)

        results, total = await invitation_repo.search_by_user(
            email="nomatch@example.com", user_id=declining_user,
        )
        assert total >= 1
        assert any(i.id == inv.id for i in results)

    async def test_search_by_user_link_invitation_excluded(
        self, invitation_repo: SqlInvitationRepository, make_link_invitation, make_org
    ) -> None:
        org = await make_org()
        await make_link_invitation(org_id=org.id)
        results, total = await invitation_repo.search_by_user(email="nobody@example.com")
        assert total == 0
        assert len(results) == 0

    async def test_search_by_user_pagination(
        self, invitation_repo: SqlInvitationRepository, make_invitation, make_org
    ) -> None:
        org = await make_org()
        for _ in range(5):
            await make_invitation(org_id=org.id, email="page@example.com")
        results, total = await invitation_repo.search_by_user(
            email="page@example.com", limit=2,
        )
        assert total >= 5
        assert len(results) == 2

    async def test_search_by_user_filter_by_org_id(
        self, invitation_repo: SqlInvitationRepository, make_invitation, make_org
    ) -> None:
        org1 = await make_org()
        org2 = await make_org()
        inv1 = await make_invitation(org_id=org1.id, email="filter-org@example.com")
        await make_invitation(org_id=org2.id, email="filter-org@example.com")

        results, total = await invitation_repo.search_by_user(
            email="filter-org@example.com",
            filters={"org_id": str(org1.id)},
        )
        assert total >= 1
        assert any(i.id == inv1.id for i in results)
        assert not any(i.org_id == org2.id for i in results)

    async def test_search_by_user_filter_by_status(
        self, invitation_repo: SqlInvitationRepository, make_invitation, make_org
    ) -> None:
        org = await make_org()
        inv = await make_invitation(org_id=org.id, email="status-filter@example.com")
        accepting_user = Id.generate()
        inv.accept(user_id=accepting_user)
        inv.clear_domain_events()
        await invitation_repo.update(inv)

        results, total = await invitation_repo.search_by_user(
            email="status-filter@example.com",
            user_id=accepting_user,
            filters={"status": "accepted"},
        )
        assert total >= 1
        assert all(i.status == InvitationStatus.ACCEPTED for i in results)

    async def test_search_by_user_total_count(
        self, invitation_repo: SqlInvitationRepository, make_invitation, make_org
    ) -> None:
        org = await make_org()
        for i in range(3):
            await make_invitation(org_id=org.id, email="total@example.com")
        _, total = await invitation_repo.search_by_user(email="total@example.com")
        assert total >= 3


@pytest.mark.integration
class TestSqlInvitationRepositoryDelete:
    """Тесты удаления."""

    async def test_delete(self, invitation_repo: SqlInvitationRepository, make_invitation) -> None:
        inv = await make_invitation()
        await invitation_repo.delete(inv.id)
        found = await invitation_repo.get_by_id(inv.id)
        assert found is None

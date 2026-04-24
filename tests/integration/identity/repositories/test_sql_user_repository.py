"""Интеграционные тесты SqlUserRepository (реальная PostgreSQL)."""

import pytest

from app.shared.domain.value_objects.email_vo import Email
from app.shared.domain.value_objects.id_vo import Id
from app.context.identity.domain.aggregates.user import User
from app.context.identity.domain.value_objects.account_status import AccountStatus
from app.context.identity.domain.value_objects.auth_provider import AuthProvider
from app.context.identity.infrastructure.persistence.repositories.sql_user_repository import SqlUserRepository


@pytest.mark.integration
class TestSqlUserRepositoryAdd:
    """Тесты добавления пользователя."""

    async def test_add_and_get_by_id(self, user_repo: SqlUserRepository, make_user) -> None:
        user = await make_user()
        found = await user_repo.get_by_id(user.id)
        assert found is not None
        assert found.id == user.id
        assert found.email == user.email

    async def test_add_persists_status(self, user_repo: SqlUserRepository, make_user) -> None:
        user = await make_user()
        found = await user_repo.get_by_id(user.id)
        assert found is not None
        assert found.status == AccountStatus.PENDING_VERIFICATION


@pytest.mark.integration
class TestSqlUserRepositoryGetByEmail:
    """Тесты поиска по email."""

    async def test_get_by_email_found(self, user_repo: SqlUserRepository, make_user) -> None:
        user = await make_user(email="findme@test.com")
        found = await user_repo.get_by_email(Email("findme@test.com"))
        assert found is not None
        assert found.id == user.id

    async def test_get_by_email_not_found(self, user_repo: SqlUserRepository) -> None:
        found = await user_repo.get_by_email(Email("nobody@test.com"))
        assert found is None


@pytest.mark.integration
class TestSqlUserRepositoryGetByRole:
    """Тесты поиска по роли."""

    async def test_get_by_role(self, user_repo: SqlUserRepository, make_user, make_role) -> None:
        role = await make_role(name="editor")
        user = await make_user()
        user.assign_role(role.id)
        user.clear_domain_events()
        await user_repo.update(user)

        found = await user_repo.get_by_role(role.id)
        assert len(found) >= 1
        assert any(u.id == user.id for u in found)

    async def test_get_by_role_empty(self, user_repo: SqlUserRepository) -> None:
        found = await user_repo.get_by_role(Id.generate())
        assert found == []


@pytest.mark.integration
class TestSqlUserRepositoryUpdate:
    """Тесты обновления пользователя."""

    async def test_update_status(self, user_repo: SqlUserRepository, make_user) -> None:
        user = await make_user()
        user.confirm_email()
        user.clear_domain_events()
        await user_repo.update(user)

        found = await user_repo.get_by_id(user.id)
        assert found is not None
        assert found.status == AccountStatus.ACTIVE
        assert found.is_email_confirmed is True

    async def test_update_role_sync(self, user_repo: SqlUserRepository, make_user, make_role) -> None:
        role1 = await make_role(name="role-a")
        role2 = await make_role(name="role-b")
        user = await make_user()

        user.assign_role(role1.id)
        user.assign_role(role2.id)
        user.clear_domain_events()
        await user_repo.update(user)

        found = await user_repo.get_by_id(user.id)
        assert found is not None
        assert len(found.role_ids) == 2

        # Убираем одну роль
        found.remove_role(role1.id)
        found.clear_domain_events()
        await user_repo.update(found)

        reloaded = await user_repo.get_by_id(user.id)
        assert reloaded is not None
        assert len(reloaded.role_ids) == 1
        assert reloaded.role_ids[0] == role2.id


@pytest.mark.integration
class TestSqlUserRepositoryDelete:
    """Тесты удаления."""

    async def test_delete(self, user_repo: SqlUserRepository, make_user) -> None:
        user = await make_user()
        await user_repo.delete(user.id)
        found = await user_repo.get_by_id(user.id)
        assert found is None


@pytest.mark.integration
class TestSqlUserRepositorySearch:
    """Тесты поиска и пагинации."""

    async def test_get_all(self, user_repo: SqlUserRepository, make_user) -> None:
        await make_user()
        await make_user()
        users = await user_repo.get_all(offset=0, limit=100)
        assert len(users) >= 2

    async def test_get_paginated(self, user_repo: SqlUserRepository, make_user) -> None:
        await make_user()
        await make_user()
        await make_user()
        users, total = await user_repo.get_paginated(page=1, page_size=2)
        assert len(users) <= 2
        assert total >= 3

    async def test_search_with_filters(self, user_repo: SqlUserRepository, make_user) -> None:
        user = await make_user()
        results = await user_repo.search(
            filters={"status": AccountStatus.PENDING_VERIFICATION.value},
            offset=0,
            limit=100,
        )
        assert len(results) >= 1

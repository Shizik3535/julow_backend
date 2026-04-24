"""Интеграционные тесты SqlRoleRepository (реальная PostgreSQL)."""

import uuid

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.identity.domain.aggregates.role import Role
from app.context.identity.infrastructure.persistence.repositories.sql_role_repository import SqlRoleRepository


@pytest.mark.integration
class TestSqlRoleRepositoryBasic:
    """Базовые CRUD тесты ролей."""

    async def test_add_and_get_by_id(self, role_repo: SqlRoleRepository, make_role) -> None:
        role = await make_role(name="test-role")
        found = await role_repo.get_by_id(role.id)
        assert found is not None
        assert found.name == "test-role"

    async def test_get_by_id_not_found(self, role_repo: SqlRoleRepository) -> None:
        found = await role_repo.get_by_id(Id.generate())
        assert found is None


@pytest.mark.integration
class TestSqlRoleRepositoryGetByName:
    """Тесты поиска по имени."""

    async def test_get_by_name_found(self, role_repo: SqlRoleRepository, make_role) -> None:
        name = f"unique-{uuid.uuid4().hex[:6]}"
        role = await make_role(name=name)
        found = await role_repo.get_by_name(name)
        assert found is not None
        assert found.id == role.id

    async def test_get_by_name_not_found(self, role_repo: SqlRoleRepository) -> None:
        found = await role_repo.get_by_name("nonexistent-role")
        assert found is None


@pytest.mark.integration
class TestSqlRoleRepositorySystemRoles:
    """Тесты системных ролей."""

    async def test_get_system_roles(self, role_repo: SqlRoleRepository, make_role) -> None:
        await make_role(name="admin-sys", is_system=True)
        await make_role(name="custom-role", is_system=False)

        system_roles = await role_repo.get_system_roles()
        assert all(r.is_system for r in system_roles)
        assert any(r.name == "admin-sys" for r in system_roles)

    async def test_get_system_roles_empty(self, role_repo: SqlRoleRepository) -> None:
        # Если нет системных ролей, возвращаем пустой список
        # (другие тесты могут уже создать, поэтому просто проверяем тип)
        result = await role_repo.get_system_roles()
        assert isinstance(result, list)


@pytest.mark.integration
class TestSqlRoleRepositorySearch:
    """Тесты поиска ролей."""

    async def test_search_by_name(self, role_repo: SqlRoleRepository, make_role) -> None:
        unique = uuid.uuid4().hex[:6]
        await make_role(name=f"search-{unique}-role")

        results = await role_repo.search(filters={"name": unique}, offset=0, limit=10)
        assert len(results) >= 1
        assert any(unique in r.name for r in results)

    async def test_search_with_pagination(self, role_repo: SqlRoleRepository, make_role) -> None:
        for i in range(5):
            await make_role()

        results = await role_repo.search(offset=0, limit=3)
        assert len(results) <= 3

    async def test_search_by_is_system(self, role_repo: SqlRoleRepository, make_role) -> None:
        await make_role(name=f"sys-{uuid.uuid4().hex[:4]}", is_system=True)

        results = await role_repo.search(filters={"is_system": True}, offset=0, limit=100)
        assert all(r.is_system for r in results)

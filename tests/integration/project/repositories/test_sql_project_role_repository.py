"""Интеграционные тесты SqlProjectRoleRepository (реальная PostgreSQL)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.domain.aggregates.project_role import ProjectRole
from app.context.project.infrastructure.persistence.repositories.sql_project_role_repository import SqlProjectRoleRepository


@pytest.mark.integration
class TestSqlProjectRoleRepositoryAdd:
    """Тесты добавления."""

    async def test_add_and_get_by_id(self, role_repo: SqlProjectRoleRepository, make_project_role) -> None:
        role = await make_project_role()
        found = await role_repo.get_by_id(role.id)
        assert found is not None
        assert found.id == role.id

    async def test_add_persists_attributes(self, role_repo: SqlProjectRoleRepository, make_project_role) -> None:
        role = await make_project_role(name="CustomRole", permissions=["tasks.read", "tasks.write"])
        found = await role_repo.get_by_id(role.id)
        assert found is not None
        assert found.name == "CustomRole"
        assert "tasks.read" in found.permissions
        assert found.is_system is False


@pytest.mark.integration
class TestSqlProjectRoleRepositorySearch:
    """Тесты поиска."""

    async def test_get_by_project(self, role_repo: SqlProjectRoleRepository, make_project_role) -> None:
        role = await make_project_role()
        roles = await role_repo.get_by_project(role.project_id)
        assert len(roles) >= 1
        assert any(r.id == role.id for r in roles)

    async def test_get_by_name(self, role_repo: SqlProjectRoleRepository, make_project_with_membership) -> None:
        proj_data = await make_project_with_membership()
        owner_role_id = proj_data["system_roles"][0].id
        found = await role_repo.get_by_name("owner")
        assert found is not None
        assert found.name == "owner"
        assert found.id == owner_role_id

    async def test_get_by_name_not_found(self, role_repo: SqlProjectRoleRepository) -> None:
        found = await role_repo.get_by_name("nonexistent-role")
        assert found is None


@pytest.mark.integration
class TestSqlProjectRoleRepositoryUpdate:
    """Тесты обновления."""

    async def test_update_permissions(self, role_repo: SqlProjectRoleRepository, make_project_role) -> None:
        role = await make_project_role(permissions=["tasks.read"])
        role.update(permissions=["tasks.read", "tasks.write", "members.*"])
        role.clear_domain_events()
        await role_repo.update(role)

        found = await role_repo.get_by_id(role.id)
        assert found is not None
        assert "members.*" in found.permissions


@pytest.mark.integration
class TestSqlProjectRoleRepositoryDelete:
    """Тесты удаления."""

    async def test_delete(self, role_repo: SqlProjectRoleRepository, make_project_role) -> None:
        role = await make_project_role()
        await role_repo.delete(role.id)
        found = await role_repo.get_by_id(role.id)
        assert found is None

    async def test_get_by_id_not_found(self, role_repo: SqlProjectRoleRepository) -> None:
        found = await role_repo.get_by_id(Id.generate())
        assert found is None

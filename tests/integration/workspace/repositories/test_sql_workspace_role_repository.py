"""Интеграционные тесты SqlWorkspaceRoleRepository (реальная PostgreSQL)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.domain.aggregates.workspace_role import WorkspaceRole
from app.context.workspace.infrastructure.persistence.repositories.sql_workspace_role_repository import (
    SqlWorkspaceRoleRepository,
)


@pytest.mark.integration
class TestSqlWorkspaceRoleRepositoryAdd:
    """Тесты добавления WorkspaceRole."""

    async def test_add_and_get_by_id(self, ws_role_repo: SqlWorkspaceRoleRepository, make_workspace) -> None:
        ws = await make_workspace()
        role = WorkspaceRole.create_custom(
            workspace_id=ws.id, name="custom-role", permissions=["members.read"]
        )
        role.clear_domain_events()
        await ws_role_repo.add(role)

        found = await ws_role_repo.get_by_id(role.id)
        assert found is not None
        assert found.id == role.id

    async def test_add_persists_attributes(self, ws_role_repo: SqlWorkspaceRoleRepository, make_workspace) -> None:
        ws = await make_workspace()
        role = WorkspaceRole.create_custom(
            workspace_id=ws.id, name="editor", permissions=["members.read", "members.write"], description="Editor role"
        )
        role.clear_domain_events()
        await ws_role_repo.add(role)

        found = await ws_role_repo.get_by_id(role.id)
        assert found is not None
        assert found.name == "editor"
        assert found.permissions == ["members.read", "members.write"]
        assert found.is_system is False
        assert found.description == "Editor role"

    async def test_add_system_role(self, ws_role_repo: SqlWorkspaceRoleRepository) -> None:
        role = WorkspaceRole.create_system(
            name="sys-role", permissions=["ws.*"], description="System role"
        )
        role.clear_domain_events()
        await ws_role_repo.add(role)

        found = await ws_role_repo.get_by_id(role.id)
        assert found is not None
        assert found.is_system is True
        assert found.workspace_id is None


@pytest.mark.integration
class TestSqlWorkspaceRoleRepositorySearch:
    """Тесты поиска WorkspaceRole."""

    async def test_get_by_name(self, ws_role_repo: SqlWorkspaceRoleRepository, make_workspace) -> None:
        ws = await make_workspace()
        role = WorkspaceRole.create_custom(
            workspace_id=ws.id, name="unique-role-name", permissions=["members.read"]
        )
        role.clear_domain_events()
        await ws_role_repo.add(role)

        found = await ws_role_repo.get_by_name("unique-role-name")
        assert found is not None
        assert found.id == role.id

    async def test_get_by_name_not_found(self, ws_role_repo: SqlWorkspaceRoleRepository) -> None:
        found = await ws_role_repo.get_by_name("nonexistent-role")
        assert found is None

    async def test_get_system_roles(self, ws_role_repo: SqlWorkspaceRoleRepository) -> None:
        role = WorkspaceRole.create_system(name="sys-test", permissions=["ws.*"])
        role.clear_domain_events()
        await ws_role_repo.add(role)

        result = await ws_role_repo.get_system_roles()
        assert len(result) >= 1
        assert all(r.is_system for r in result)

    async def test_get_by_workspace(self, ws_role_repo: SqlWorkspaceRoleRepository, make_workspace) -> None:
        ws = await make_workspace()
        custom_role = WorkspaceRole.create_custom(
            workspace_id=ws.id, name="ws-custom", permissions=["members.read"]
        )
        custom_role.clear_domain_events()
        await ws_role_repo.add(custom_role)

        result = await ws_role_repo.get_by_workspace(ws.id)
        names = [r.name for r in result]
        assert "ws-custom" in names

    async def test_search_by_name(self, ws_role_repo: SqlWorkspaceRoleRepository, make_workspace) -> None:
        ws = await make_workspace()
        role = WorkspaceRole.create_custom(
            workspace_id=ws.id, name="searchable-role", permissions=["members.read"]
        )
        role.clear_domain_events()
        await ws_role_repo.add(role)

        result = await ws_role_repo.search(filters={"name": "searchable"})
        assert len(result) >= 1

    async def test_search_by_is_system(self, ws_role_repo: SqlWorkspaceRoleRepository) -> None:
        result = await ws_role_repo.search(filters={"is_system": True})
        assert all(r.is_system for r in result)

    async def test_search_pagination(self, ws_role_repo: SqlWorkspaceRoleRepository) -> None:
        result = await ws_role_repo.search(offset=0, limit=2)
        assert len(result) <= 2


@pytest.mark.integration
class TestSqlWorkspaceRoleRepositoryUpdate:
    """Тесты обновления WorkspaceRole."""

    async def test_update_permissions(self, ws_role_repo: SqlWorkspaceRoleRepository, make_workspace) -> None:
        ws = await make_workspace()
        role = WorkspaceRole.create_custom(
            workspace_id=ws.id, name="updatable-role", permissions=["members.read"]
        )
        role.clear_domain_events()
        await ws_role_repo.add(role)

        role.update(permissions=["members.read", "members.write", "teams.read"])
        role.clear_domain_events()
        await ws_role_repo.update(role)

        found = await ws_role_repo.get_by_id(role.id)
        assert found is not None
        assert found.permissions == ["members.read", "members.write", "teams.read"]

    async def test_update_description(self, ws_role_repo: SqlWorkspaceRoleRepository, make_workspace) -> None:
        ws = await make_workspace()
        role = WorkspaceRole.create_custom(
            workspace_id=ws.id, name="desc-role", permissions=["members.read"]
        )
        role.clear_domain_events()
        await ws_role_repo.add(role)

        role.update(description="Updated description")
        role.clear_domain_events()
        await ws_role_repo.update(role)

        found = await ws_role_repo.get_by_id(role.id)
        assert found is not None
        assert found.description == "Updated description"


@pytest.mark.integration
class TestSqlWorkspaceRoleRepositoryDelete:
    """Тесты удаления WorkspaceRole."""

    async def test_delete(self, ws_role_repo: SqlWorkspaceRoleRepository, make_workspace) -> None:
        ws = await make_workspace()
        role = WorkspaceRole.create_custom(
            workspace_id=ws.id, name="deletable-role", permissions=["members.read"]
        )
        role.clear_domain_events()
        await ws_role_repo.add(role)

        await ws_role_repo.delete(role.id)
        found = await ws_role_repo.get_by_id(role.id)
        assert found is None

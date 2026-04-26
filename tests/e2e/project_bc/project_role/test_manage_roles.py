"""E2E-тесты: POST/PATCH/DELETE /workspaces/{ws_id}/projects/{project_id}/roles — Управление ролями проекта."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    register_and_login,
    add_project_member_with_role
)


@pytest.mark.e2e
class TestCreateProjectRole:
    """Создание кастомной роли проекта (roles.*)."""

    async def test_create_role_success_admin(self, client: AsyncClient, project_owner):
        """201 — admin создаёт кастомную роль (roles.*)."""
        proj = project_owner
        admin = await register_and_login(client)
        await add_project_member_with_role(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            owner_token=proj["access_token"],
            new_member_user_id=admin["user_id"],
            role_name="admin"
        )
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/roles",
            json={"name": "Developer", "permissions": ["tasks.read", "tasks.create"], "description": "Dev role"},
            headers=auth_headers(admin["access_token"])
        )
        assert resp.status_code == 201

    async def test_create_role_success_owner(self, client: AsyncClient, project_owner):
        """201 — owner создаёт кастомную роль (project.*)."""
        proj = project_owner
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/roles",
            json={"name": "Developer", "permissions": ["tasks.read", "tasks.create"], "description": "Dev role"},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 201

    async def test_create_role_forbidden_manager(self, client: AsyncClient, project_owner):
        """403 — manager (нет roles.*)."""
        proj = project_owner
        manager = await register_and_login(client)
        await add_project_member_with_role(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            owner_token=proj["access_token"],
            new_member_user_id=manager["user_id"],
            role_name="manager"
        )
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/roles",
            json={"name": "Developer", "permissions": ["tasks.read"]},
            headers=auth_headers(manager["access_token"])
        )
        assert resp.status_code == 403

    async def test_create_role_no_auth(self, client: AsyncClient, project_owner):
        """401 — без токена."""
        proj = project_owner
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/roles",
            json={"name": "Developer", "permissions": ["tasks.read"]}
        )
        assert resp.status_code == 401


@pytest.mark.e2e
class TestUpdateProjectRole:
    """Обновление роли проекта (roles.*)."""

    async def test_update_role_success_admin(self, client: AsyncClient, project_owner):
        """200 — admin обновляет кастомную роль."""
        proj = project_owner
        admin = await register_and_login(client)
        await add_project_member_with_role(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            owner_token=proj["access_token"],
            new_member_user_id=admin["user_id"],
            role_name="admin"
        )
        create_resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/roles",
            json={"name": "Developer", "permissions": ["tasks.read"], "description": "Dev"},
            headers=auth_headers(proj["access_token"])
        )
        role_id = create_resp.json()["data"]["id"]
        resp = await client.patch(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/roles/{role_id}",
            json={"permissions": ["tasks.read", "tasks.create", "tasks.update"], "description": "Full dev"},
            headers=auth_headers(admin["access_token"])
        )
        assert resp.status_code == 200

    async def test_update_role_forbidden_manager(self, client: AsyncClient, project_owner):
        """403 — manager (нет roles.*)."""
        proj = project_owner
        manager = await register_and_login(client)
        await add_project_member_with_role(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            owner_token=proj["access_token"],
            new_member_user_id=manager["user_id"],
            role_name="manager"
        )
        create_resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/roles",
            json={"name": "DevRole", "permissions": ["tasks.read"]},
            headers=auth_headers(proj["access_token"])
        )
        role_id = create_resp.json()["data"]["id"]
        resp = await client.patch(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/roles/{role_id}",
            json={"permissions": ["tasks.read"]},
            headers=auth_headers(manager["access_token"])
        )
        assert resp.status_code == 403


@pytest.mark.e2e
class TestDeleteProjectRole:
    """Удаление роли проекта (roles.*)."""
    async def test_delete_role_forbidden_manager(self, client: AsyncClient, project_owner):
        """403 — manager (нет roles.*)."""
        proj = project_owner
        manager = await register_and_login(client)
        await add_project_member_with_role(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            owner_token=proj["access_token"],
            new_member_user_id=manager["user_id"],
            role_name="manager"
        )
        create_resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/roles",
            json={"name": "TempRole", "permissions": ["tasks.read"]},
            headers=auth_headers(proj["access_token"])
        )
        role_id = create_resp.json()["data"]["id"]
        resp = await client.delete(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/roles/{role_id}",
            headers=auth_headers(manager["access_token"])
        )
        assert resp.status_code == 403
    async def test_delete_system_role_conflict(self, client: AsyncClient, project_owner):
        """409 — нельзя удалить системную роль."""
        proj = project_owner
        # Get system owner role id
        roles_resp = await client.get(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/roles",
            headers=auth_headers(proj["access_token"])
        )
        roles = roles_resp.json().get("data", [])
        owner_role_id = ""
        for r in roles:
            if r.get("name") == "owner":
                owner_role_id = r.get("id", "")
                break
        resp = await client.delete(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/roles/{owner_role_id}",
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 409
    async def test_delete_role_no_auth(self, client: AsyncClient, project_owner):
        """401 — без токена."""
        proj = project_owner
        resp = await client.delete(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/roles/00000000-0000-0000-0000-000000000000"
        )
        assert resp.status_code == 401
    async def test_delete_role_success_admin(self, client: AsyncClient, project_owner):
        """200 — admin удаляет кастомную роль."""
        proj = project_owner
        admin = await register_and_login(client)
        await add_project_member_with_role(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            owner_token=proj["access_token"],
            new_member_user_id=admin["user_id"],
            role_name="admin"
        )
        create_resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/roles",
            json={"name": "TempRole", "permissions": ["tasks.read"]},
            headers=auth_headers(proj["access_token"])
        )
        role_id = create_resp.json()["data"]["id"]
        resp = await client.delete(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/roles/{role_id}",
            headers=auth_headers(admin["access_token"])
        )
        assert resp.status_code == 200

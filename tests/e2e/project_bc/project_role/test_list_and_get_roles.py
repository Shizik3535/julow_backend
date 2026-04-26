"""E2E-тесты: GET /workspaces/{ws_id}/projects/{project_id}/roles — Роли проекта."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    register_and_login,
    add_project_member_with_role
)


@pytest.mark.e2e
class TestListProjectRoles:
    """Список ролей проекта (roles.read)."""

    async def test_list_roles_success_admin(self, client: AsyncClient, project_owner):
        """200 — admin получает список ролей (roles.*)."""
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
        resp = await client.get(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/roles",
            headers=auth_headers(admin["access_token"])
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert isinstance(data, list)
        assert len(data) >= 5  # 5 system roles

    async def test_list_roles_success_owner(self, client: AsyncClient, project_owner):
        """200 — owner получает список ролей (project.*)."""
        proj = project_owner
        resp = await client.get(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/roles",
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 200

    async def test_list_roles_no_auth(self, client: AsyncClient, project_owner):
        """401 — без токена."""
        proj = project_owner
        resp = await client.get(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/roles"
        )
        assert resp.status_code == 401


@pytest.mark.e2e
class TestGetProjectRole:
    """Получение конкретной роли проекта (roles.read)."""

    async def test_get_role_success_admin(self, client: AsyncClient, project_owner):
        """200 — admin получает роль."""
        proj = project_owner
        admin = await register_and_login(client)
        add_result = await add_project_member_with_role(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            owner_token=proj["access_token"],
            new_member_user_id=admin["user_id"],
            role_name="admin"
        )
        role_id = add_result["role_id"]
        resp = await client.get(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/roles/{role_id}",
            headers=auth_headers(admin["access_token"])
        )
        assert resp.status_code == 200

    async def test_get_role_no_auth(self, client: AsyncClient, project_owner):
        """401 — без токена."""
        proj = project_owner
        resp = await client.get(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/roles/00000000-0000-0000-0000-000000000000"
        )
        assert resp.status_code == 401

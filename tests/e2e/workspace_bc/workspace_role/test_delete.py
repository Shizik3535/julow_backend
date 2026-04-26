import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    register_and_login,
    add_ws_member_with_role
)


@pytest.mark.e2e
class TestDeleteWorkspaceRole:
    """DELETE /workspaces/{ws_id}/roles/{role_id} — Удалить роль (roles.write)."""
    async def test_delete_role_no_auth(self, client: AsyncClient, workspace_owner):
        """401 — без токена."""
        ws = workspace_owner
        resp = await client.delete(
            f"{API}/workspaces/{ws['ws_id']}/roles/00000000-0000-0000-0000-000000000000"
        )
        assert resp.status_code == 401
    async def test_delete_role_forbidden_system_role(self, client: AsyncClient, workspace_owner):
        """403 — попытка удалить системную роль."""
        ws = workspace_owner
        roles_resp = await client.get(
            f"{API}/workspaces/{ws['ws_id']}/roles",
            params={"system_only": True},
            headers=auth_headers(ws["access_token"])
        )
        items = roles_resp.json()["items"]
        system_role_id = items[0]["id"]
        resp = await client.delete(
            f"{API}/workspaces/{ws['ws_id']}/roles/{system_role_id}",
            headers=auth_headers(ws["access_token"])
        )
        assert resp.status_code == 403
    async def test_delete_role_forbidden_manager(self, client: AsyncClient, workspace_owner):
        """403 — manager."""
        ws = workspace_owner
        manager = await register_and_login(client)
        await add_ws_member_with_role(
            client,
            ws_id=ws["ws_id"],
            owner_token=ws["access_token"],
            new_member_user_id=manager["user_id"],
            role_name="manager"
        )
        create_resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/roles",
            json={"name": "mgr-deletable", "permissions": ["teams.read"]},
            headers=auth_headers(ws["access_token"])
        )
        role_id = create_resp.json()["data"]["id"]
        resp = await client.delete(
            f"{API}/workspaces/{ws['ws_id']}/roles/{role_id}",
            headers=auth_headers(manager["access_token"])
        )
        assert resp.status_code == 403
    async def test_delete_role_not_found(self, client: AsyncClient, workspace_owner):
        """404 — роль не найдена."""
        ws = workspace_owner
        resp = await client.delete(
            f"{API}/workspaces/{ws['ws_id']}/roles/00000000-0000-0000-0000-000000000000",
            headers=auth_headers(ws["access_token"])
        )
        assert resp.status_code == 404
    async def test_delete_role_success_owner(self, client: AsyncClient, workspace_owner):
        """200 — owner удаляет кастомную роль."""
        ws = workspace_owner
        create_resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/roles",
            json={"name": "deletable-role", "permissions": ["members.read"]},
            headers=auth_headers(ws["access_token"])
        )
        role_id = create_resp.json()["data"]["id"]
        resp = await client.delete(
            f"{API}/workspaces/{ws['ws_id']}/roles/{role_id}",
            headers=auth_headers(ws["access_token"])
        )
        assert resp.status_code == 200
    async def test_delete_role_success_admin(self, client: AsyncClient, workspace_owner):
        """200 — admin удаляет."""
        ws = workspace_owner
        admin = await register_and_login(client)
        await add_ws_member_with_role(
            client,
            ws_id=ws["ws_id"],
            owner_token=ws["access_token"],
            new_member_user_id=admin["user_id"],
            role_name="admin"
        )
        create_resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/roles",
            json={"name": "admin-deletable", "permissions": ["teams.read"]},
            headers=auth_headers(ws["access_token"])
        )
        role_id = create_resp.json()["data"]["id"]
        resp = await client.delete(
            f"{API}/workspaces/{ws['ws_id']}/roles/{role_id}",
            headers=auth_headers(admin["access_token"])
        )
        assert resp.status_code == 200

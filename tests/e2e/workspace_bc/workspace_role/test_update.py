import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    register_and_login,
    add_ws_member_with_role
)


@pytest.mark.e2e
class TestUpdateWorkspaceRole:
    """PATCH /workspaces/{ws_id}/roles/{role_id} — Обновить роль (roles.write)."""

    async def test_update_role_success_owner(self, client: AsyncClient, workspace_owner):
        """200 — owner обновляет permissions кастомной роли."""
        ws = workspace_owner
        create_resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/roles",
            json={"name": "updatable-role", "permissions": ["members.read"]},
            headers=auth_headers(ws["access_token"])
        )
        role_id = create_resp.json()["data"]["id"]
        resp = await client.patch(
            f"{API}/workspaces/{ws['ws_id']}/roles/{role_id}",
            json={"permissions": ["members.read", "members.write"], "description": "Updated"},
            headers=auth_headers(ws["access_token"])
        )
        assert resp.status_code == 200

    async def test_update_role_success_admin(self, client: AsyncClient, workspace_owner):
        """200 — admin обновляет."""
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
            json={"name": "admin-updatable", "permissions": ["teams.read"]},
            headers=auth_headers(ws["access_token"])
        )
        role_id = create_resp.json()["data"]["id"]
        resp = await client.patch(
            f"{API}/workspaces/{ws['ws_id']}/roles/{role_id}",
            json={"permissions": ["teams.read", "teams.write"]},
            headers=auth_headers(admin["access_token"])
        )
        assert resp.status_code == 200

    async def test_update_role_no_auth(self, client: AsyncClient, workspace_owner):
        """401 — без токена."""
        ws = workspace_owner
        resp = await client.patch(
            f"{API}/workspaces/{ws['ws_id']}/roles/00000000-0000-0000-0000-000000000000",
            json={"permissions": ["members.read"]}
        )
        assert resp.status_code == 401

    async def test_update_role_forbidden_system_role(self, client: AsyncClient, workspace_owner):
        """403 — попытка обновить системную роль (workspace_id=None)."""
        ws = workspace_owner
        roles_resp = await client.get(
            f"{API}/workspaces/{ws['ws_id']}/roles",
            params={"system_only": True},
            headers=auth_headers(ws["access_token"])
        )
        items = roles_resp.json()["items"]
        system_role_id = items[0]["id"]
        resp = await client.patch(
            f"{API}/workspaces/{ws['ws_id']}/roles/{system_role_id}",
            json={"permissions": ["ws.*"]},
            headers=auth_headers(ws["access_token"])
        )
        assert resp.status_code == 403

    async def test_update_role_forbidden_manager(self, client: AsyncClient, workspace_owner):
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
            json={"name": "mgr-role", "permissions": ["teams.read"]},
            headers=auth_headers(ws["access_token"])
        )
        role_id = create_resp.json()["data"]["id"]
        resp = await client.patch(
            f"{API}/workspaces/{ws['ws_id']}/roles/{role_id}",
            json={"permissions": ["teams.write"]},
            headers=auth_headers(manager["access_token"])
        )
        assert resp.status_code == 403

    async def test_update_role_not_found(self, client: AsyncClient, workspace_owner):
        """404 — роль не найдена."""
        ws = workspace_owner
        resp = await client.patch(
            f"{API}/workspaces/{ws['ws_id']}/roles/00000000-0000-0000-0000-000000000000",
            json={"permissions": ["members.read"]},
            headers=auth_headers(ws["access_token"])
        )
        assert resp.status_code == 404

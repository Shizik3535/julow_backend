import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    create_workspace_with_owner,
    register_and_login,
    add_ws_member_with_role,
)


@pytest.mark.e2e
class TestGetWorkspaceRole:
    """GET /workspaces/{ws_id}/roles/{role_id} — Данные роли (roles.read для кастомных, без проверки для системных)."""

    async def test_get_system_role_success(self, client: AsyncClient):
        """200 — системная роль (без проверки permission)."""
        ws = await create_workspace_with_owner(client)
        roles_resp = await client.get(
            f"{API}/workspaces/{ws['ws_id']}/roles",
            params={"system_only": True},
            headers=auth_headers(ws["access_token"]),
        )
        items = roles_resp.json()["items"]
        assert len(items) > 0
        role_id = items[0]["id"]
        resp = await client.get(
            f"{API}/workspaces/{ws['ws_id']}/roles/{role_id}",
            headers=auth_headers(ws["access_token"]),
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["id"] == role_id

    async def test_get_custom_role_success(self, client: AsyncClient):
        """200 — кастомная роль (с roles.read)."""
        ws = await create_workspace_with_owner(client)
        # Создаём кастомную роль
        create_resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/roles",
            json={"name": "custom-role", "permissions": ["members.read"]},
            headers=auth_headers(ws["access_token"]),
        )
        assert create_resp.status_code == 201
        role_id = create_resp.json()["data"]["id"]
        resp = await client.get(
            f"{API}/workspaces/{ws['ws_id']}/roles/{role_id}",
            headers=auth_headers(ws["access_token"]),
        )
        assert resp.status_code == 200

    async def test_get_custom_role_forbidden(self, client: AsyncClient):
        """403 — кастомная роль, нет roles.read."""
        ws = await create_workspace_with_owner(client)
        create_resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/roles",
            json={"name": "custom-role-2", "permissions": ["members.read"]},
            headers=auth_headers(ws["access_token"]),
        )
        role_id = create_resp.json()["data"]["id"]
        member = await register_and_login(client)
        await add_ws_member_with_role(
            client,
            ws_id=ws["ws_id"],
            owner_token=ws["access_token"],
            new_member_user_id=member["user_id"],
            role_name="member",
        )
        resp = await client.get(
            f"{API}/workspaces/{ws['ws_id']}/roles/{role_id}",
            headers=auth_headers(member["access_token"]),
        )
        assert resp.status_code == 403

    async def test_get_role_no_auth(self, client: AsyncClient):
        """401 — без токена."""
        ws = await create_workspace_with_owner(client)
        resp = await client.get(
            f"{API}/workspaces/{ws['ws_id']}/roles/00000000-0000-0000-0000-000000000000",
        )
        assert resp.status_code == 401

    async def test_get_role_not_found(self, client: AsyncClient):
        """404 — роль не найдена."""
        ws = await create_workspace_with_owner(client)
        resp = await client.get(
            f"{API}/workspaces/{ws['ws_id']}/roles/00000000-0000-0000-0000-000000000000",
            headers=auth_headers(ws["access_token"]),
        )
        assert resp.status_code == 404

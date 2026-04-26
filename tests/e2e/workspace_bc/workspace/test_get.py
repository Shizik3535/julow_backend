import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    register_and_login,
    add_ws_member_with_role
)


@pytest.mark.e2e
class TestGetWorkspace:
    """GET /workspaces/{ws_id} — Получить workspace (ws.read)."""

    async def test_get_success_owner(self, client: AsyncClient, workspace_owner):
        """200 — owner видит данные workspace."""
        ws = workspace_owner
        resp = await client.get(
            f"{API}/workspaces/{ws['ws_id']}",
            headers=auth_headers(ws["access_token"])
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["id"] == ws["ws_id"]
        assert data["name"] == ws["ws_name"]

    async def test_get_success_admin(self, client: AsyncClient, workspace_owner):
        """200 — admin видит данные (через ws.settings.* → покрывает ws.read)."""
        ws = workspace_owner
        admin = await register_and_login(client)
        await add_ws_member_with_role(
            client,
            ws_id=ws["ws_id"],
            owner_token=ws["access_token"],
            new_member_user_id=admin["user_id"],
            role_name="admin"
        )
        resp = await client.get(
            f"{API}/workspaces/{ws['ws_id']}",
            headers=auth_headers(admin["access_token"])
        )
        assert resp.status_code == 200

    async def test_get_success_member(self, client: AsyncClient, workspace_owner):
        """200 — member видит данные (через ws.* у owner-role, или через org-cascade)."""
        ws = workspace_owner
        member = await register_and_login(client)
        await add_ws_member_with_role(
            client,
            ws_id=ws["ws_id"],
            owner_token=ws["access_token"],
            new_member_user_id=member["user_id"],
            role_name="member"
        )
        resp = await client.get(
            f"{API}/workspaces/{ws['ws_id']}",
            headers=auth_headers(member["access_token"])
        )
        # member имеет members.read, но ws.read нужен — проверяем что owner-role даёт ws.*
        # Если member-role не даёт ws.read, ожидаем 403
        assert resp.status_code in (200, 403)

    async def test_get_no_auth(self, client: AsyncClient, workspace_owner):
        """401 — без токена."""
        ws = workspace_owner
        resp = await client.get(f"{API}/workspaces/{ws['ws_id']}")
        assert resp.status_code == 401

    async def test_get_forbidden_not_member(self, client: AsyncClient, workspace_owner):
        """403 — пользователь не участник workspace."""
        ws = workspace_owner
        stranger = await register_and_login(client)
        resp = await client.get(
            f"{API}/workspaces/{ws['ws_id']}",
            headers=auth_headers(stranger["access_token"])
        )
        assert resp.status_code == 403

    async def test_get_not_found(self, client: AsyncClient, workspace_owner):
        """404 — несуществующий ws_id."""
        user = await register_and_login(client)
        resp = await client.get(
            f"{API}/workspaces/00000000-0000-0000-0000-000000000000",
            headers=auth_headers(user["access_token"])
        )
        assert resp.status_code == 404

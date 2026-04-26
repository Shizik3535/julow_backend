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
class TestGetWorkspaceMember:
    """GET /workspaces/{ws_id}/members/{user_id} — Данные участника (members.read)."""

    async def test_get_member_success_owner(self, client: AsyncClient):
        """200 — owner получает данные участника."""
        ws = await create_workspace_with_owner(client)
        resp = await client.get(
            f"{API}/workspaces/{ws['ws_id']}/members/{ws['user_id']}",
            headers=auth_headers(ws["access_token"]),
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["user_id"] == ws["user_id"]

    async def test_get_member_success_member(self, client: AsyncClient):
        """200 — member получает данные другого участника."""
        ws = await create_workspace_with_owner(client)
        member = await register_and_login(client)
        await add_ws_member_with_role(
            client,
            ws_id=ws["ws_id"],
            owner_token=ws["access_token"],
            new_member_user_id=member["user_id"],
            role_name="member",
        )
        resp = await client.get(
            f"{API}/workspaces/{ws['ws_id']}/members/{ws['user_id']}",
            headers=auth_headers(member["access_token"]),
        )
        assert resp.status_code == 200

    async def test_get_member_no_auth(self, client: AsyncClient):
        """401 — без токена."""
        ws = await create_workspace_with_owner(client)
        resp = await client.get(
            f"{API}/workspaces/{ws['ws_id']}/members/{ws['user_id']}",
        )
        assert resp.status_code == 401

    async def test_get_member_forbidden_not_member(self, client: AsyncClient):
        """403 — не участник workspace."""
        ws = await create_workspace_with_owner(client)
        stranger = await register_and_login(client)
        resp = await client.get(
            f"{API}/workspaces/{ws['ws_id']}/members/{ws['user_id']}",
            headers=auth_headers(stranger["access_token"]),
        )
        assert resp.status_code == 403

    async def test_get_member_not_found(self, client: AsyncClient):
        """404 — участник не найден."""
        ws = await create_workspace_with_owner(client)
        resp = await client.get(
            f"{API}/workspaces/{ws['ws_id']}/members/00000000-0000-0000-0000-000000000000",
            headers=auth_headers(ws["access_token"]),
        )
        assert resp.status_code == 404

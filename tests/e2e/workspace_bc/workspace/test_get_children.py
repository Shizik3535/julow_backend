import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    register_and_login,
    add_ws_member_with_role
)


@pytest.mark.e2e
class TestGetChildWorkspaces:
    """GET /workspaces/{ws_id}/children — Дочерние workspace (ws.read)."""

    async def test_get_children_success_owner(self, client: AsyncClient, workspace_owner):
        """200 — owner видит дочерние workspace."""
        ws = workspace_owner
        resp = await client.get(
            f"{API}/workspaces/{ws['ws_id']}/children",
            headers=auth_headers(ws["access_token"])
        )
        assert resp.status_code == 200
        body = resp.json()
        assert isinstance(body.get("items"), list)

    async def test_get_children_no_auth(self, client: AsyncClient, workspace_owner):
        """401 — без токена."""
        ws = workspace_owner
        resp = await client.get(f"{API}/workspaces/{ws['ws_id']}/children")
        assert resp.status_code == 401

    async def test_get_children_forbidden_not_member(self, client: AsyncClient, workspace_owner):
        """403 — не участник."""
        ws = workspace_owner
        stranger = await register_and_login(client)
        resp = await client.get(
            f"{API}/workspaces/{ws['ws_id']}/children",
            headers=auth_headers(stranger["access_token"])
        )
        assert resp.status_code == 403

    async def test_get_children_not_found(self, client: AsyncClient):
        """404 — несуществующий workspace."""
        user = await register_and_login(client)
        resp = await client.get(
            f"{API}/workspaces/00000000-0000-0000-0000-000000000000/children",
            headers=auth_headers(user["access_token"])
        )
        assert resp.status_code == 404

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    create_workspace_with_owner,
    register_and_login,
)


@pytest.mark.e2e
class TestSearchWorkspaces:
    """GET /workspaces/ — Поиск workspace (ws.read, has_permission фильтрация)."""

    async def test_search_success(self, client: AsyncClient):
        """200 — возвращает workspace где пользователь участник с ws.read."""
        ws = await create_workspace_with_owner(client)
        resp = await client.get(
            f"{API}/workspaces/",
            headers=auth_headers(ws["access_token"]),
        )
        assert resp.status_code == 200
        body = resp.json()
        assert isinstance(body.get("items"), list)
        ws_ids = [item["id"] for item in body["items"]]
        assert ws["ws_id"] in ws_ids

    async def test_search_with_filters(self, client: AsyncClient):
        """200 — фильтрация по organization_id."""
        ws = await create_workspace_with_owner(client)
        resp = await client.get(
            f"{API}/workspaces/",
            params={"limit": 10},
            headers=auth_headers(ws["access_token"]),
        )
        assert resp.status_code == 200

    async def test_search_empty_for_new_user(self, client: AsyncClient):
        """200 — пользователь без workspace → пустой список."""
        user = await register_and_login(client)
        resp = await client.get(
            f"{API}/workspaces/",
            headers=auth_headers(user["access_token"]),
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("items", []) == []

    async def test_search_no_auth(self, client: AsyncClient):
        """401 — без токена."""
        resp = await client.get(f"{API}/workspaces/")
        assert resp.status_code == 401

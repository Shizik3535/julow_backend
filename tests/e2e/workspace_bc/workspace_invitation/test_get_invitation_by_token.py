import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers
)


def _member_role_id(roles_resp):
    items = roles_resp.json()["items"]
    return next(r["id"] for r in items if r["name"] == "member")


@pytest.mark.e2e
class TestGetWorkspaceInvitationByToken:
    """GET /workspaces/invitations/token/{token} — Данные приглашения по токену (без авторизации!)."""

    async def test_get_by_token_success(self, client: AsyncClient, workspace_owner):
        """200 — данные приглашения по токену (без авторизации)."""
        ws = workspace_owner
        roles_resp = await client.get(
            f"{API}/workspaces/{ws['ws_id']}/roles",
            params={"system_only": True},
            headers=auth_headers(ws["access_token"])
        )
        role_id = _member_role_id(roles_resp)
        link_resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/invitations/link",
            json={"role_id": role_id},
            headers=auth_headers(ws["access_token"])
        )
        assert link_resp.status_code == 201
        token = link_resp.json()["data"]["link"]["value"]
        resp = await client.get(f"{API}/workspaces/invitations/token/{token}")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["link"]["value"] == token

    async def test_get_by_token_not_found(self, client: AsyncClient):
        """404 — токен не найден."""
        resp = await client.get(
            f"{API}/workspaces/invitations/token/nonexistent-token-12345"
        )
        assert resp.status_code == 404

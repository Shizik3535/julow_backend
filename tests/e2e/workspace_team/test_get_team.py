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
class TestGetWorkspaceTeam:
    """GET /workspaces/{ws_id}/teams/{team_id} — Данные команды (teams.read)."""

    async def test_get_team_success_owner(self, client: AsyncClient):
        """200 — owner получает данные команды."""
        ws = await create_workspace_with_owner(client)
        create_resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/teams",
            json={"name": "Test Team"},
            headers=auth_headers(ws["access_token"]),
        )
        assert create_resp.status_code == 201
        team_id = create_resp.json()["data"]["id"]
        resp = await client.get(
            f"{API}/workspaces/{ws['ws_id']}/teams/{team_id}",
            headers=auth_headers(ws["access_token"]),
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["id"] == team_id

    async def test_get_team_success_manager(self, client: AsyncClient):
        """200 — manager получает данные."""
        ws = await create_workspace_with_owner(client)
        manager = await register_and_login(client)
        await add_ws_member_with_role(
            client,
            ws_id=ws["ws_id"],
            owner_token=ws["access_token"],
            new_member_user_id=manager["user_id"],
            role_name="manager",
        )
        create_resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/teams",
            json={"name": "Mgr Team"},
            headers=auth_headers(ws["access_token"]),
        )
        team_id = create_resp.json()["data"]["id"]
        resp = await client.get(
            f"{API}/workspaces/{ws['ws_id']}/teams/{team_id}",
            headers=auth_headers(manager["access_token"]),
        )
        assert resp.status_code == 200

    async def test_get_team_no_auth(self, client: AsyncClient):
        """401 — без токена."""
        ws = await create_workspace_with_owner(client)
        resp = await client.get(
            f"{API}/workspaces/{ws['ws_id']}/teams/00000000-0000-0000-0000-000000000000",
        )
        assert resp.status_code == 401

    async def test_get_team_forbidden_member(self, client: AsyncClient):
        """403 — member."""
        ws = await create_workspace_with_owner(client)
        member = await register_and_login(client)
        await add_ws_member_with_role(
            client,
            ws_id=ws["ws_id"],
            owner_token=ws["access_token"],
            new_member_user_id=member["user_id"],
            role_name="member",
        )
        create_resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/teams",
            json={"name": "Member Team"},
            headers=auth_headers(ws["access_token"]),
        )
        team_id = create_resp.json()["data"]["id"]
        resp = await client.get(
            f"{API}/workspaces/{ws['ws_id']}/teams/{team_id}",
            headers=auth_headers(member["access_token"]),
        )
        assert resp.status_code == 403

    async def test_get_team_not_found(self, client: AsyncClient):
        """404 — команда не найдена."""
        ws = await create_workspace_with_owner(client)
        resp = await client.get(
            f"{API}/workspaces/{ws['ws_id']}/teams/00000000-0000-0000-0000-000000000000",
            headers=auth_headers(ws["access_token"]),
        )
        assert resp.status_code == 404

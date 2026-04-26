import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    register_and_login,
    add_ws_member_with_role
)


@pytest.mark.e2e
class TestUpdateWorkspaceTeam:
    """PATCH /workspaces/{ws_id}/teams/{team_id} — Обновить команду (teams.write)."""

    async def test_update_team_success_owner(self, client: AsyncClient, workspace_owner):
        """200 — owner обновляет."""
        ws = workspace_owner
        create_resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/teams",
            json={"name": "Old Team"},
            headers=auth_headers(ws["access_token"])
        )
        team_id = create_resp.json()["data"]["id"]
        resp = await client.patch(
            f"{API}/workspaces/{ws['ws_id']}/teams/{team_id}",
            json={"name": "New Team Name"},
            headers=auth_headers(ws["access_token"])
        )
        assert resp.status_code == 200

    async def test_update_team_success_manager(self, client: AsyncClient, workspace_owner):
        """200 — manager обновляет."""
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
            f"{API}/workspaces/{ws['ws_id']}/teams",
            json={"name": "Mgr Team"},
            headers=auth_headers(ws["access_token"])
        )
        team_id = create_resp.json()["data"]["id"]
        resp = await client.patch(
            f"{API}/workspaces/{ws['ws_id']}/teams/{team_id}",
            json={"name": "Mgr Updated"},
            headers=auth_headers(manager["access_token"])
        )
        assert resp.status_code == 200

    async def test_update_team_no_auth(self, client: AsyncClient, workspace_owner):
        """401 — без токена."""
        ws = workspace_owner
        resp = await client.patch(
            f"{API}/workspaces/{ws['ws_id']}/teams/00000000-0000-0000-0000-000000000000",
            json={"name": "No Auth"}
        )
        assert resp.status_code == 401

    async def test_update_team_forbidden_member(self, client: AsyncClient, workspace_owner):
        """403 — member."""
        ws = workspace_owner
        member = await register_and_login(client)
        await add_ws_member_with_role(
            client,
            ws_id=ws["ws_id"],
            owner_token=ws["access_token"],
            new_member_user_id=member["user_id"],
            role_name="member"
        )
        create_resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/teams",
            json={"name": "Team"},
            headers=auth_headers(ws["access_token"])
        )
        team_id = create_resp.json()["data"]["id"]
        resp = await client.patch(
            f"{API}/workspaces/{ws['ws_id']}/teams/{team_id}",
            json={"name": "Member Update"},
            headers=auth_headers(member["access_token"])
        )
        assert resp.status_code == 403

    async def test_update_team_not_found(self, client: AsyncClient, workspace_owner):
        """404 — команда не найдена."""
        ws = workspace_owner
        resp = await client.patch(
            f"{API}/workspaces/{ws['ws_id']}/teams/00000000-0000-0000-0000-000000000000",
            json={"name": "Not Found"},
            headers=auth_headers(ws["access_token"])
        )
        assert resp.status_code == 404

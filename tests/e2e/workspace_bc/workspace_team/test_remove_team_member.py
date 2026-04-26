import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    register_and_login,
    register_user,
    add_ws_member_with_role
)


@pytest.mark.e2e
class TestRemoveWorkspaceTeamMember:
    """DELETE /workspaces/{ws_id}/teams/{team_id}/members/{user_id} — Удалить из команды (teams.write)."""

    async def test_remove_team_member_success_owner(self, client: AsyncClient, workspace_owner):
        """200 — owner удаляет из команды."""
        ws = workspace_owner
        new_user = await register_user(client)
        await add_ws_member_with_role(
            client,
            ws_id=ws["ws_id"],
            owner_token=ws["access_token"],
            new_member_user_id=new_user["user_id"],
            role_name="member"
        )
        create_resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/teams",
            json={"name": "Remove Team"},
            headers=auth_headers(ws["access_token"])
        )
        team_id = create_resp.json()["data"]["id"]
        await client.post(
            f"{API}/workspaces/{ws['ws_id']}/teams/{team_id}/members/{new_user['user_id']}",
            headers=auth_headers(ws["access_token"])
        )
        resp = await client.delete(
            f"{API}/workspaces/{ws['ws_id']}/teams/{team_id}/members/{new_user['user_id']}",
            headers=auth_headers(ws["access_token"])
        )
        assert resp.status_code == 200

    async def test_remove_team_member_success_manager(self, client: AsyncClient, workspace_owner):
        """200 — manager удаляет."""
        ws = workspace_owner
        manager = await register_and_login(client)
        await add_ws_member_with_role(
            client,
            ws_id=ws["ws_id"],
            owner_token=ws["access_token"],
            new_member_user_id=manager["user_id"],
            role_name="manager"
        )
        new_user = await register_user(client)
        await add_ws_member_with_role(
            client,
            ws_id=ws["ws_id"],
            owner_token=ws["access_token"],
            new_member_user_id=new_user["user_id"],
            role_name="member"
        )
        create_resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/teams",
            json={"name": "Mgr Remove Team"},
            headers=auth_headers(ws["access_token"])
        )
        team_id = create_resp.json()["data"]["id"]
        await client.post(
            f"{API}/workspaces/{ws['ws_id']}/teams/{team_id}/members/{new_user['user_id']}",
            headers=auth_headers(ws["access_token"])
        )
        resp = await client.delete(
            f"{API}/workspaces/{ws['ws_id']}/teams/{team_id}/members/{new_user['user_id']}",
            headers=auth_headers(manager["access_token"])
        )
        assert resp.status_code == 200

    async def test_remove_team_member_no_auth(self, client: AsyncClient, workspace_owner):
        """401 — без токена."""
        ws = workspace_owner
        resp = await client.delete(
            f"{API}/workspaces/{ws['ws_id']}/teams/00000000-0000-0000-0000-000000000000/members/{ws['user_id']}"
        )
        assert resp.status_code == 401

    async def test_remove_team_member_forbidden_member(self, client: AsyncClient, workspace_owner):
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
            json={"name": "Member Remove Team"},
            headers=auth_headers(ws["access_token"])
        )
        team_id = create_resp.json()["data"]["id"]
        resp = await client.delete(
            f"{API}/workspaces/{ws['ws_id']}/teams/{team_id}/members/{ws['user_id']}",
            headers=auth_headers(member["access_token"])
        )
        assert resp.status_code == 403

    async def test_remove_team_member_not_found(self, client: AsyncClient, workspace_owner):
        """404 — команда не найдена."""
        ws = workspace_owner
        resp = await client.delete(
            f"{API}/workspaces/{ws['ws_id']}/teams/00000000-0000-0000-0000-000000000000/members/{ws['user_id']}",
            headers=auth_headers(ws["access_token"])
        )
        assert resp.status_code == 404

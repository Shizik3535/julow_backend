import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    create_workspace_with_owner,
    register_and_login,
    register_user,
    add_ws_member_with_role,
)


@pytest.mark.e2e
class TestAddWorkspaceTeamMember:
    """POST /workspaces/{ws_id}/teams/{team_id}/members/{user_id} — Добавить в команду (teams.write)."""

    async def test_add_team_member_success_owner(self, client: AsyncClient):
        """200 — owner добавляет участника в команду."""
        ws = await create_workspace_with_owner(client)
        new_user = await register_user(client)
        await add_ws_member_with_role(
            client,
            ws_id=ws["ws_id"],
            owner_token=ws["access_token"],
            new_member_user_id=new_user["user_id"],
            role_name="member",
        )
        create_resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/teams",
            json={"name": "Team For Add"},
            headers=auth_headers(ws["access_token"]),
        )
        team_id = create_resp.json()["data"]["id"]
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/teams/{team_id}/members/{new_user['user_id']}",
            headers=auth_headers(ws["access_token"]),
        )
        assert resp.status_code == 200

    async def test_add_team_member_success_manager(self, client: AsyncClient):
        """200 — manager добавляет."""
        ws = await create_workspace_with_owner(client)
        manager = await register_and_login(client)
        await add_ws_member_with_role(
            client,
            ws_id=ws["ws_id"],
            owner_token=ws["access_token"],
            new_member_user_id=manager["user_id"],
            role_name="manager",
        )
        new_user = await register_user(client)
        await add_ws_member_with_role(
            client,
            ws_id=ws["ws_id"],
            owner_token=ws["access_token"],
            new_member_user_id=new_user["user_id"],
            role_name="member",
        )
        create_resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/teams",
            json={"name": "Mgr Add Team"},
            headers=auth_headers(ws["access_token"]),
        )
        team_id = create_resp.json()["data"]["id"]
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/teams/{team_id}/members/{new_user['user_id']}",
            headers=auth_headers(manager["access_token"]),
        )
        assert resp.status_code == 200

    async def test_add_team_member_no_auth(self, client: AsyncClient):
        """401 — без токена."""
        ws = await create_workspace_with_owner(client)
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/teams/00000000-0000-0000-0000-000000000000/members/{ws['user_id']}",
        )
        assert resp.status_code == 401

    async def test_add_team_member_forbidden_member(self, client: AsyncClient):
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
            json={"name": "Member Add Team"},
            headers=auth_headers(ws["access_token"]),
        )
        team_id = create_resp.json()["data"]["id"]
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/teams/{team_id}/members/{ws['user_id']}",
            headers=auth_headers(member["access_token"]),
        )
        assert resp.status_code == 403

    async def test_add_team_member_not_found_team(self, client: AsyncClient):
        """404 — команда не найдена."""
        ws = await create_workspace_with_owner(client)
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/teams/00000000-0000-0000-0000-000000000000/members/{ws['user_id']}",
            headers=auth_headers(ws["access_token"]),
        )
        assert resp.status_code == 404

    async def test_add_team_member_conflict_already_in_team(self, client: AsyncClient):
        """409 — участник уже в команде."""
        ws = await create_workspace_with_owner(client)
        new_user = await register_user(client)
        await add_ws_member_with_role(
            client,
            ws_id=ws["ws_id"],
            owner_token=ws["access_token"],
            new_member_user_id=new_user["user_id"],
            role_name="member",
        )
        create_resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/teams",
            json={"name": "Dup Team"},
            headers=auth_headers(ws["access_token"]),
        )
        team_id = create_resp.json()["data"]["id"]
        await client.post(
            f"{API}/workspaces/{ws['ws_id']}/teams/{team_id}/members/{new_user['user_id']}",
            headers=auth_headers(ws["access_token"]),
        )
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/teams/{team_id}/members/{new_user['user_id']}",
            headers=auth_headers(ws["access_token"]),
        )
        assert resp.status_code == 409

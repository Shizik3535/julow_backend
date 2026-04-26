import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    register_and_login,
    add_ws_member_with_role
)


@pytest.mark.e2e
class TestGetWorkspaceTeams:
    """GET /workspaces/{ws_id}/teams — Список команд (teams.read)."""

    async def test_get_teams_success_owner(self, client: AsyncClient, workspace_owner):
        """200 — owner видит команды."""
        ws = workspace_owner
        resp = await client.get(
            f"{API}/workspaces/{ws['ws_id']}/teams",
            headers=auth_headers(ws["access_token"])
        )
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data.get("items"), list)

    async def test_get_teams_success_admin(self, client: AsyncClient, workspace_owner):
        """200 — admin видит (через teams.*)."""
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
            f"{API}/workspaces/{ws['ws_id']}/teams",
            headers=auth_headers(admin["access_token"])
        )
        assert resp.status_code == 200

    async def test_get_teams_success_manager(self, client: AsyncClient, workspace_owner):
        """200 — manager видит (через teams.*)."""
        ws = workspace_owner
        manager = await register_and_login(client)
        await add_ws_member_with_role(
            client,
            ws_id=ws["ws_id"],
            owner_token=ws["access_token"],
            new_member_user_id=manager["user_id"],
            role_name="manager"
        )
        resp = await client.get(
            f"{API}/workspaces/{ws['ws_id']}/teams",
            headers=auth_headers(manager["access_token"])
        )
        assert resp.status_code == 200

    async def test_get_teams_no_auth(self, client: AsyncClient, workspace_owner):
        """401 — без токена."""
        ws = workspace_owner
        resp = await client.get(f"{API}/workspaces/{ws['ws_id']}/teams")
        assert resp.status_code == 401

    async def test_get_teams_forbidden_member(self, client: AsyncClient, workspace_owner):
        """403 — member (нет teams.read)."""
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
            f"{API}/workspaces/{ws['ws_id']}/teams",
            headers=auth_headers(member["access_token"])
        )
        assert resp.status_code == 403

    async def test_get_teams_not_found(self, client: AsyncClient):
        """404 — несуществующий workspace."""
        user = await register_and_login(client)
        resp = await client.get(
            f"{API}/workspaces/00000000-0000-0000-0000-000000000000/teams",
            headers=auth_headers(user["access_token"])
        )
        assert resp.status_code == 404

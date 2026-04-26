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
class TestDeactivateWorkspaceTeam:
    """POST /workspaces/{ws_id}/teams/{team_id}/deactivate — Деактивировать (teams.write)."""

    async def test_deactivate_success_owner(self, client: AsyncClient):
        """200 — owner деактивирует."""
        ws = await create_workspace_with_owner(client)
        create_resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/teams",
            json={"name": "Deactivate Team"},
            headers=auth_headers(ws["access_token"]),
        )
        team_id = create_resp.json()["data"]["id"]
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/teams/{team_id}/deactivate",
            headers=auth_headers(ws["access_token"]),
        )
        assert resp.status_code == 200

    async def test_deactivate_success_manager(self, client: AsyncClient):
        """200 — manager деактивирует."""
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
            json={"name": "Mgr Deact Team"},
            headers=auth_headers(ws["access_token"]),
        )
        team_id = create_resp.json()["data"]["id"]
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/teams/{team_id}/deactivate",
            headers=auth_headers(manager["access_token"]),
        )
        assert resp.status_code == 200

    async def test_deactivate_no_auth(self, client: AsyncClient):
        """401 — без токена."""
        ws = await create_workspace_with_owner(client)
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/teams/00000000-0000-0000-0000-000000000000/deactivate",
        )
        assert resp.status_code == 401

    async def test_deactivate_forbidden_member(self, client: AsyncClient):
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
            json={"name": "Member Deact Team"},
            headers=auth_headers(ws["access_token"]),
        )
        team_id = create_resp.json()["data"]["id"]
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/teams/{team_id}/deactivate",
            headers=auth_headers(member["access_token"]),
        )
        assert resp.status_code == 403

    async def test_deactivate_not_found(self, client: AsyncClient):
        """404 — команда не найдена."""
        ws = await create_workspace_with_owner(client)
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/teams/00000000-0000-0000-0000-000000000000/deactivate",
            headers=auth_headers(ws["access_token"]),
        )
        assert resp.status_code == 404

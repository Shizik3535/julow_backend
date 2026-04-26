import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    register_and_login,
    add_ws_member_with_role
)


@pytest.mark.e2e
class TestGetWorkspaceRoles:
    """GET /workspaces/{ws_id}/roles — Список ролей (roles.read)."""

    async def test_get_roles_success_owner(self, client: AsyncClient, workspace_owner):
        """200 — owner видит все роли."""
        ws = workspace_owner
        resp = await client.get(
            f"{API}/workspaces/{ws['ws_id']}/roles",
            headers=auth_headers(ws["access_token"])
        )
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data.get("items"), list)

    async def test_get_roles_success_admin(self, client: AsyncClient, workspace_owner):
        """200 — admin видит (через roles.*)."""
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
            f"{API}/workspaces/{ws['ws_id']}/roles",
            headers=auth_headers(admin["access_token"])
        )
        assert resp.status_code == 200

    async def test_get_roles_system_only(self, client: AsyncClient, workspace_owner):
        """200 — только системные роли (system_only=true)."""
        ws = workspace_owner
        resp = await client.get(
            f"{API}/workspaces/{ws['ws_id']}/roles",
            params={"system_only": True},
            headers=auth_headers(ws["access_token"])
        )
        assert resp.status_code == 200
        items = resp.json()["items"]
        assert len(items) > 0

    async def test_get_roles_no_auth(self, client: AsyncClient, workspace_owner):
        """401 — без токена."""
        ws = workspace_owner
        resp = await client.get(f"{API}/workspaces/{ws['ws_id']}/roles")
        assert resp.status_code == 401

    async def test_get_roles_forbidden_manager(self, client: AsyncClient, workspace_owner):
        """403 — manager (нет roles.read)."""
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
            f"{API}/workspaces/{ws['ws_id']}/roles",
            headers=auth_headers(manager["access_token"])
        )
        assert resp.status_code == 403

    async def test_get_roles_forbidden_member(self, client: AsyncClient, workspace_owner):
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
        resp = await client.get(
            f"{API}/workspaces/{ws['ws_id']}/roles",
            headers=auth_headers(member["access_token"])
        )
        assert resp.status_code == 403

    async def test_get_roles_not_found(self, client: AsyncClient):
        """404 — несуществующий workspace."""
        user = await register_and_login(client)
        resp = await client.get(
            f"{API}/workspaces/00000000-0000-0000-0000-000000000000/roles",
            headers=auth_headers(user["access_token"])
        )
        assert resp.status_code == 404

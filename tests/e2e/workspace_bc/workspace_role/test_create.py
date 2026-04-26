import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    register_and_login,
    add_ws_member_with_role
)


@pytest.mark.e2e
class TestCreateWorkspaceRole:
    """POST /workspaces/{ws_id}/roles — Создать кастомную роль (roles.write)."""

    async def test_create_role_success_owner(self, client: AsyncClient, workspace_owner):
        """201 — owner создаёт кастомную роль."""
        ws = workspace_owner
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/roles",
            json={"name": "custom-editor", "permissions": ["members.read", "members.write"]},
            headers=auth_headers(ws["access_token"])
        )
        assert resp.status_code == 201
        data = resp.json()["data"]
        assert data["name"] == "custom-editor"

    async def test_create_role_success_admin(self, client: AsyncClient, workspace_owner):
        """201 — admin создаёт (через roles.*)."""
        ws = workspace_owner
        admin = await register_and_login(client)
        await add_ws_member_with_role(
            client,
            ws_id=ws["ws_id"],
            owner_token=ws["access_token"],
            new_member_user_id=admin["user_id"],
            role_name="admin"
        )
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/roles",
            json={"name": "admin-role", "permissions": ["teams.read"]},
            headers=auth_headers(admin["access_token"])
        )
        assert resp.status_code == 201

    async def test_create_role_no_auth(self, client: AsyncClient, workspace_owner):
        """401 — без токена."""
        ws = workspace_owner
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/roles",
            json={"name": "no-auth-role", "permissions": ["members.read"]}
        )
        assert resp.status_code == 401

    async def test_create_role_forbidden_manager(self, client: AsyncClient, workspace_owner):
        """403 — manager (нет roles.write)."""
        ws = workspace_owner
        manager = await register_and_login(client)
        await add_ws_member_with_role(
            client,
            ws_id=ws["ws_id"],
            owner_token=ws["access_token"],
            new_member_user_id=manager["user_id"],
            role_name="manager"
        )
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/roles",
            json={"name": "manager-role", "permissions": ["members.read"]},
            headers=auth_headers(manager["access_token"])
        )
        assert resp.status_code == 403

    async def test_create_role_forbidden_member(self, client: AsyncClient, workspace_owner):
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
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/roles",
            json={"name": "member-role", "permissions": ["members.read"]},
            headers=auth_headers(member["access_token"])
        )
        assert resp.status_code == 403

    async def test_create_role_not_found_workspace(self, client: AsyncClient):
        """404 — несуществующий workspace."""
        user = await register_and_login(client)
        resp = await client.post(
            f"{API}/workspaces/00000000-0000-0000-0000-000000000000/roles",
            json={"name": "ghost-role", "permissions": ["members.read"]},
            headers=auth_headers(user["access_token"])
        )
        assert resp.status_code == 404

    async def test_create_role_conflict_duplicate_name(self, client: AsyncClient, workspace_owner):
        """409 — роль с таким именем уже существует."""
        ws = workspace_owner
        await client.post(
            f"{API}/workspaces/{ws['ws_id']}/roles",
            json={"name": "duplicate-role", "permissions": ["members.read"]},
            headers=auth_headers(ws["access_token"])
        )
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/roles",
            json={"name": "duplicate-role", "permissions": ["members.write"]},
            headers=auth_headers(ws["access_token"])
        )
        assert resp.status_code == 409

    async def test_create_role_validation_missing_name(self, client: AsyncClient, workspace_owner):
        """422 — отсутствует name."""
        ws = workspace_owner
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/roles",
            json={"permissions": ["members.read"]},
            headers=auth_headers(ws["access_token"])
        )
        assert resp.status_code == 422

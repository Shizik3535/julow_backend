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
class TestChangeWorkspaceMemberRole:
    """PATCH /workspaces/{ws_id}/members/{user_id}/role — Смена роли (members.write)."""

    async def test_change_role_success_owner(self, client: AsyncClient):
        """200 — owner меняет роль участника."""
        ws = await create_workspace_with_owner(client)
        new_user = await register_user(client)
        result = await add_ws_member_with_role(
            client,
            ws_id=ws["ws_id"],
            owner_token=ws["access_token"],
            new_member_user_id=new_user["user_id"],
            role_name="member",
        )
        # Находим роль admin
        roles_resp = await client.get(
            f"{API}/workspaces/{ws['ws_id']}/roles",
            params={"system_only": True},
            headers=auth_headers(ws["access_token"]),
        )
        roles = roles_resp.json()["items"]
        admin_role_id = next(r["id"] for r in roles if r["name"] == "admin")
        resp = await client.patch(
            f"{API}/workspaces/{ws['ws_id']}/members/{new_user['user_id']}/role",
            json={"new_role_id": admin_role_id},
            headers=auth_headers(ws["access_token"]),
        )
        assert resp.status_code == 200

    async def test_change_role_success_admin(self, client: AsyncClient):
        """200 — admin меняет роль."""
        ws = await create_workspace_with_owner(client)
        admin = await register_and_login(client)
        await add_ws_member_with_role(
            client,
            ws_id=ws["ws_id"],
            owner_token=ws["access_token"],
            new_member_user_id=admin["user_id"],
            role_name="admin",
        )
        new_user = await register_user(client)
        await add_ws_member_with_role(
            client,
            ws_id=ws["ws_id"],
            owner_token=ws["access_token"],
            new_member_user_id=new_user["user_id"],
            role_name="member",
        )
        # Находим роль manager
        roles_resp = await client.get(
            f"{API}/workspaces/{ws['ws_id']}/roles",
            params={"system_only": True},
            headers=auth_headers(ws["access_token"]),
        )
        roles = roles_resp.json()["items"]
        manager_role_id = next(r["id"] for r in roles if r["name"] == "manager")
        resp = await client.patch(
            f"{API}/workspaces/{ws['ws_id']}/members/{new_user['user_id']}/role",
            json={"new_role_id": manager_role_id},
            headers=auth_headers(admin["access_token"]),
        )
        assert resp.status_code == 200

    async def test_change_role_no_auth(self, client: AsyncClient):
        """401 — без токена."""
        ws = await create_workspace_with_owner(client)
        resp = await client.patch(
            f"{API}/workspaces/{ws['ws_id']}/members/{ws['user_id']}/role",
            json={"new_role_id": "00000000-0000-0000-0000-000000000000"},
        )
        assert resp.status_code == 401

    async def test_change_role_forbidden_manager(self, client: AsyncClient):
        """403 — manager (нет members.write)."""
        ws = await create_workspace_with_owner(client)
        manager = await register_and_login(client)
        await add_ws_member_with_role(
            client,
            ws_id=ws["ws_id"],
            owner_token=ws["access_token"],
            new_member_user_id=manager["user_id"],
            role_name="manager",
        )
        resp = await client.patch(
            f"{API}/workspaces/{ws['ws_id']}/members/{ws['user_id']}/role",
            json={"new_role_id": "00000000-0000-0000-0000-000000000000"},
            headers=auth_headers(manager["access_token"]),
        )
        assert resp.status_code == 403

    async def test_change_role_forbidden_member(self, client: AsyncClient):
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
        resp = await client.patch(
            f"{API}/workspaces/{ws['ws_id']}/members/{ws['user_id']}/role",
            json={"new_role_id": "00000000-0000-0000-0000-000000000000"},
            headers=auth_headers(member["access_token"]),
        )
        assert resp.status_code == 403

    async def test_change_role_not_found(self, client: AsyncClient):
        """404 — несуществующий участник."""
        ws = await create_workspace_with_owner(client)
        resp = await client.patch(
            f"{API}/workspaces/{ws['ws_id']}/members/00000000-0000-0000-0000-000000000000/role",
            json={"new_role_id": "00000000-0000-0000-0000-000000000000"},
            headers=auth_headers(ws["access_token"]),
        )
        assert resp.status_code == 404

    async def test_change_role_validation_missing_role(self, client: AsyncClient):
        """422 — отсутствует new_role_id."""
        ws = await create_workspace_with_owner(client)
        resp = await client.patch(
            f"{API}/workspaces/{ws['ws_id']}/members/{ws['user_id']}/role",
            json={},
            headers=auth_headers(ws["access_token"]),
        )
        assert resp.status_code == 422

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
class TestRemoveWorkspaceMember:
    """DELETE /workspaces/{ws_id}/members/{user_id} — Удалить участника (members.write)."""

    async def test_remove_member_success_owner(self, client: AsyncClient):
        """200 — owner удаляет участника."""
        ws = await create_workspace_with_owner(client)
        new_user = await register_user(client)
        await add_ws_member_with_role(
            client,
            ws_id=ws["ws_id"],
            owner_token=ws["access_token"],
            new_member_user_id=new_user["user_id"],
            role_name="member",
        )
        resp = await client.delete(
            f"{API}/workspaces/{ws['ws_id']}/members/{new_user['user_id']}",
            headers=auth_headers(ws["access_token"]),
        )
        assert resp.status_code == 200

    async def test_remove_member_success_admin(self, client: AsyncClient):
        """200 — admin удаляет."""
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
        resp = await client.delete(
            f"{API}/workspaces/{ws['ws_id']}/members/{new_user['user_id']}",
            headers=auth_headers(admin["access_token"]),
        )
        assert resp.status_code == 200

    async def test_remove_member_no_auth(self, client: AsyncClient):
        """401 — без токена."""
        ws = await create_workspace_with_owner(client)
        resp = await client.delete(
            f"{API}/workspaces/{ws['ws_id']}/members/{ws['user_id']}",
        )
        assert resp.status_code == 401

    async def test_remove_member_forbidden_manager(self, client: AsyncClient):
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
        new_user = await register_user(client)
        await add_ws_member_with_role(
            client,
            ws_id=ws["ws_id"],
            owner_token=ws["access_token"],
            new_member_user_id=new_user["user_id"],
            role_name="member",
        )
        resp = await client.delete(
            f"{API}/workspaces/{ws['ws_id']}/members/{new_user['user_id']}",
            headers=auth_headers(manager["access_token"]),
        )
        assert resp.status_code == 403

    async def test_remove_member_forbidden_member(self, client: AsyncClient):
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
        resp = await client.delete(
            f"{API}/workspaces/{ws['ws_id']}/members/{ws['user_id']}",
            headers=auth_headers(member["access_token"]),
        )
        assert resp.status_code == 403

    async def test_remove_member_not_found(self, client: AsyncClient):
        """404 — несуществующий участник."""
        ws = await create_workspace_with_owner(client)
        resp = await client.delete(
            f"{API}/workspaces/{ws['ws_id']}/members/00000000-0000-0000-0000-000000000000",
            headers=auth_headers(ws["access_token"]),
        )
        assert resp.status_code == 404

    async def test_remove_member_conflict_last_owner(self, client: AsyncClient):
        """409 — нельзя удалить последнего владельца."""
        ws = await create_workspace_with_owner(client)
        resp = await client.delete(
            f"{API}/workspaces/{ws['ws_id']}/members/{ws['user_id']}",
            headers=auth_headers(ws["access_token"]),
        )
        assert resp.status_code == 409

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
class TestReactivateWorkspaceMember:
    """POST /workspaces/{ws_id}/members/{user_id}/reactivate — Реактивировать (members.write)."""

    async def test_reactivate_success_owner(self, client: AsyncClient):
        """200 — owner реактивирует."""
        ws = await create_workspace_with_owner(client)
        new_user = await register_user(client)
        await add_ws_member_with_role(
            client,
            ws_id=ws["ws_id"],
            owner_token=ws["access_token"],
            new_member_user_id=new_user["user_id"],
            role_name="member",
        )
        # Сначала деактивируем
        await client.post(
            f"{API}/workspaces/{ws['ws_id']}/members/{new_user['user_id']}/deactivate",
            headers=auth_headers(ws["access_token"]),
        )
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/members/{new_user['user_id']}/reactivate",
            headers=auth_headers(ws["access_token"]),
        )
        assert resp.status_code == 200

    async def test_reactivate_success_admin(self, client: AsyncClient):
        """200 — admin реактивирует."""
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
        await client.post(
            f"{API}/workspaces/{ws['ws_id']}/members/{new_user['user_id']}/deactivate",
            headers=auth_headers(ws["access_token"]),
        )
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/members/{new_user['user_id']}/reactivate",
            headers=auth_headers(admin["access_token"]),
        )
        assert resp.status_code == 200

    async def test_reactivate_no_auth(self, client: AsyncClient):
        """401 — без токена."""
        ws = await create_workspace_with_owner(client)
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/members/{ws['user_id']}/reactivate",
        )
        assert resp.status_code == 401

    async def test_reactivate_forbidden_manager(self, client: AsyncClient):
        """403 — manager."""
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
        await client.post(
            f"{API}/workspaces/{ws['ws_id']}/members/{new_user['user_id']}/deactivate",
            headers=auth_headers(ws["access_token"]),
        )
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/members/{new_user['user_id']}/reactivate",
            headers=auth_headers(manager["access_token"]),
        )
        assert resp.status_code == 403

    async def test_reactivate_not_found(self, client: AsyncClient):
        """404 — несуществующий участник."""
        ws = await create_workspace_with_owner(client)
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/members/00000000-0000-0000-0000-000000000000/reactivate",
            headers=auth_headers(ws["access_token"]),
        )
        assert resp.status_code == 404

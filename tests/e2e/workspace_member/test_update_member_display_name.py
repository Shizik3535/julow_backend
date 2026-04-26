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
class TestUpdateWorkspaceMemberDisplayName:
    """PATCH /workspaces/{ws_id}/members/{user_id}/display-name — Обновить имя (members.write)."""

    async def test_update_display_name_success_owner(self, client: AsyncClient):
        """200 — owner обновляет."""
        ws = await create_workspace_with_owner(client)
        new_user = await register_user(client)
        await add_ws_member_with_role(
            client,
            ws_id=ws["ws_id"],
            owner_token=ws["access_token"],
            new_member_user_id=new_user["user_id"],
            role_name="member",
        )
        resp = await client.patch(
            f"{API}/workspaces/{ws['ws_id']}/members/{new_user['user_id']}/display-name",
            json={"display_name": "New Display Name"},
            headers=auth_headers(ws["access_token"]),
        )
        assert resp.status_code == 200

    async def test_update_display_name_success_admin(self, client: AsyncClient):
        """200 — admin обновляет."""
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
        resp = await client.patch(
            f"{API}/workspaces/{ws['ws_id']}/members/{new_user['user_id']}/display-name",
            json={"display_name": "Admin Updated"},
            headers=auth_headers(admin["access_token"]),
        )
        assert resp.status_code == 200

    async def test_update_display_name_no_auth(self, client: AsyncClient):
        """401 — без токена."""
        ws = await create_workspace_with_owner(client)
        resp = await client.patch(
            f"{API}/workspaces/{ws['ws_id']}/members/{ws['user_id']}/display-name",
            json={"display_name": "No Auth"},
        )
        assert resp.status_code == 401

    async def test_update_display_name_forbidden_manager(self, client: AsyncClient):
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
        resp = await client.patch(
            f"{API}/workspaces/{ws['ws_id']}/members/{ws['user_id']}/display-name",
            json={"display_name": "Manager Update"},
            headers=auth_headers(manager["access_token"]),
        )
        assert resp.status_code == 403

    async def test_update_display_name_not_found(self, client: AsyncClient):
        """404 — несуществующий участник."""
        ws = await create_workspace_with_owner(client)
        resp = await client.patch(
            f"{API}/workspaces/{ws['ws_id']}/members/00000000-0000-0000-0000-000000000000/display-name",
            json={"display_name": "Not Found"},
            headers=auth_headers(ws["access_token"]),
        )
        assert resp.status_code == 404

    async def test_update_display_name_validation_empty(self, client: AsyncClient):
        """422 — пустое display_name."""
        ws = await create_workspace_with_owner(client)
        resp = await client.patch(
            f"{API}/workspaces/{ws['ws_id']}/members/{ws['user_id']}/display-name",
            json={"display_name": ""},
            headers=auth_headers(ws["access_token"]),
        )
        assert resp.status_code == 422

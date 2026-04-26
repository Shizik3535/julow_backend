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
class TestRemoveWorkspaceOwner:
    """DELETE /workspaces/{ws_id}/owners/{user_id} — Удалить со-владельца (ws.*)."""

    async def test_remove_owner_success(self, client: AsyncClient):
        """200 — owner удаляет со-владельца."""
        ws = await create_workspace_with_owner(client)
        co_owner = await register_and_login(client)
        await add_ws_member_with_role(
            client,
            ws_id=ws["ws_id"],
            owner_token=ws["access_token"],
            new_member_user_id=co_owner["user_id"],
            role_name="admin",
        )
        # Добавляем со-владельца
        await client.post(
            f"{API}/workspaces/{ws['ws_id']}/owners",
            json={"user_id": co_owner["user_id"]},
            headers=auth_headers(ws["access_token"]),
        )
        # Удаляем со-владельца
        resp = await client.delete(
            f"{API}/workspaces/{ws['ws_id']}/owners/{co_owner['user_id']}",
            headers=auth_headers(ws["access_token"]),
        )
        assert resp.status_code == 200

    async def test_remove_owner_no_auth(self, client: AsyncClient):
        """401 — без токена."""
        ws = await create_workspace_with_owner(client)
        resp = await client.delete(
            f"{API}/workspaces/{ws['ws_id']}/owners/{ws['user_id']}",
        )
        assert resp.status_code == 401

    async def test_remove_owner_forbidden_admin(self, client: AsyncClient):
        """403 — admin (нет ws.*)."""
        ws = await create_workspace_with_owner(client)
        admin = await register_and_login(client)
        await add_ws_member_with_role(
            client,
            ws_id=ws["ws_id"],
            owner_token=ws["access_token"],
            new_member_user_id=admin["user_id"],
            role_name="admin",
        )
        resp = await client.delete(
            f"{API}/workspaces/{ws['ws_id']}/owners/{ws['user_id']}",
            headers=auth_headers(admin["access_token"]),
        )
        assert resp.status_code == 403

    async def test_remove_owner_not_found(self, client: AsyncClient):
        """404 — несуществующий workspace."""
        user = await register_and_login(client)
        resp = await client.delete(
            f"{API}/workspaces/00000000-0000-0000-0000-000000000000/owners/{user['user_id']}",
            headers=auth_headers(user["access_token"]),
        )
        assert resp.status_code == 404

    async def test_remove_owner_conflict_last_owner(self, client: AsyncClient):
        """409 — нельзя удалить последнего владельца."""
        ws = await create_workspace_with_owner(client)
        resp = await client.delete(
            f"{API}/workspaces/{ws['ws_id']}/owners/{ws['user_id']}",
            headers=auth_headers(ws["access_token"]),
        )
        assert resp.status_code == 409

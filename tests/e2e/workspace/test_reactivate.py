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
class TestReactivateWorkspace:
    """POST /workspaces/{ws_id}/reactivate — Реактивировать (ws.settings.write)."""

    async def test_reactivate_success_owner(self, client: AsyncClient):
        """200 — owner реактивирует."""
        ws = await create_workspace_with_owner(client)
        await client.post(
            f"{API}/workspaces/{ws['ws_id']}/suspend",
            json={"reason": "Temp"},
            headers=auth_headers(ws["access_token"]),
        )
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/reactivate",
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
        await client.post(
            f"{API}/workspaces/{ws['ws_id']}/suspend",
            json={"reason": "Temp"},
            headers=auth_headers(ws["access_token"]),
        )
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/reactivate",
            headers=auth_headers(admin["access_token"]),
        )
        assert resp.status_code == 200

    async def test_reactivate_no_auth(self, client: AsyncClient):
        """401 — без токена."""
        ws = await create_workspace_with_owner(client)
        resp = await client.post(f"{API}/workspaces/{ws['ws_id']}/reactivate")
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
        await client.post(
            f"{API}/workspaces/{ws['ws_id']}/suspend",
            json={"reason": "Temp"},
            headers=auth_headers(ws["access_token"]),
        )
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/reactivate",
            headers=auth_headers(manager["access_token"]),
        )
        assert resp.status_code == 403

    async def test_reactivate_not_found(self, client: AsyncClient):
        """404 — несуществующий workspace."""
        user = await register_and_login(client)
        resp = await client.post(
            f"{API}/workspaces/00000000-0000-0000-0000-000000000000/reactivate",
            headers=auth_headers(user["access_token"]),
        )
        assert resp.status_code == 404

    async def test_reactivate_conflict_not_suspended(self, client: AsyncClient):
        """409 — workspace не приостановлен."""
        ws = await create_workspace_with_owner(client)
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/reactivate",
            headers=auth_headers(ws["access_token"]),
        )
        assert resp.status_code == 409

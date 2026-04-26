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
class TestMoveWorkspace:
    """POST /workspaces/{ws_id}/move — Переместить в иерархии (ws.settings.write)."""

    async def test_move_under_parent_success_owner(self, client: AsyncClient):
        """200 — owner перемещает под родительский workspace."""
        ws = await create_workspace_with_owner(client)
        parent = await create_workspace_with_owner(client)
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/move",
            json={"parent_workspace_id": parent["ws_id"]},
            headers=auth_headers(ws["access_token"]),
        )
        assert resp.status_code == 200

    async def test_move_success_admin(self, client: AsyncClient):
        """200 — admin перемещает."""
        ws = await create_workspace_with_owner(client)
        admin = await register_and_login(client)
        await add_ws_member_with_role(
            client,
            ws_id=ws["ws_id"],
            owner_token=ws["access_token"],
            new_member_user_id=admin["user_id"],
            role_name="admin",
        )
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/move",
            json={"parent_workspace_id": None},
            headers=auth_headers(admin["access_token"]),
        )
        assert resp.status_code == 200

    async def test_move_detach_from_parent(self, client: AsyncClient):
        """200 — отсоединение от родителя (parent_workspace_id=null)."""
        ws = await create_workspace_with_owner(client)
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/move",
            json={"parent_workspace_id": None},
            headers=auth_headers(ws["access_token"]),
        )
        assert resp.status_code == 200

    async def test_move_no_auth(self, client: AsyncClient):
        """401 — без токена."""
        ws = await create_workspace_with_owner(client)
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/move",
            json={"parent_workspace_id": None},
        )
        assert resp.status_code == 401

    async def test_move_forbidden_manager(self, client: AsyncClient):
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
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/move",
            json={"parent_workspace_id": None},
            headers=auth_headers(manager["access_token"]),
        )
        assert resp.status_code == 403

    async def test_move_not_found(self, client: AsyncClient):
        """404 — несуществующий workspace."""
        user = await register_and_login(client)
        resp = await client.post(
            f"{API}/workspaces/00000000-0000-0000-0000-000000000000/move",
            json={"parent_workspace_id": None},
            headers=auth_headers(user["access_token"]),
        )
        assert resp.status_code == 404

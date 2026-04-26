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
class TestTransferWorkspaceOwnership:
    """POST /workspaces/{ws_id}/transfer-ownership — Передать владение (ws.*)."""

    async def test_transfer_success_owner(self, client: AsyncClient):
        """200 — owner передаёт владение участнику."""
        ws = await create_workspace_with_owner(client)
        new_owner = await register_and_login(client)
        await add_ws_member_with_role(
            client,
            ws_id=ws["ws_id"],
            owner_token=ws["access_token"],
            new_member_user_id=new_owner["user_id"],
            role_name="admin",
        )
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/transfer-ownership",
            json={"from_id": ws["user_id"], "to_id": new_owner["user_id"]},
            headers=auth_headers(ws["access_token"]),
        )
        assert resp.status_code == 200

    async def test_transfer_no_auth(self, client: AsyncClient):
        """401 — без токена."""
        ws = await create_workspace_with_owner(client)
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/transfer-ownership",
            json={"from_id": ws["user_id"], "to_id": "some-user"},
        )
        assert resp.status_code == 401

    async def test_transfer_forbidden_admin(self, client: AsyncClient):
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
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/transfer-ownership",
            json={"from_id": ws["user_id"], "to_id": admin["user_id"]},
            headers=auth_headers(admin["access_token"]),
        )
        assert resp.status_code == 403

    async def test_transfer_forbidden_manager(self, client: AsyncClient):
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
            f"{API}/workspaces/{ws['ws_id']}/transfer-ownership",
            json={"from_id": ws["user_id"], "to_id": manager["user_id"]},
            headers=auth_headers(manager["access_token"]),
        )
        assert resp.status_code == 403

    async def test_transfer_not_found(self, client: AsyncClient):
        """404 — несуществующий workspace."""
        user = await register_and_login(client)
        resp = await client.post(
            f"{API}/workspaces/00000000-0000-0000-0000-000000000000/transfer-ownership",
            json={"from_id": user["user_id"], "to_id": "other"},
            headers=auth_headers(user["access_token"]),
        )
        assert resp.status_code == 404

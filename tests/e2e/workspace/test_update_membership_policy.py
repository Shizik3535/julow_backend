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
class TestUpdateWorkspaceMembershipPolicy:
    """PATCH /workspaces/{ws_id}/membership-policy — Обновить политику членства (ws.settings.write)."""

    async def test_update_success_owner(self, client: AsyncClient):
        """200 — owner обновляет политику членства."""
        ws = await create_workspace_with_owner(client)
        resp = await client.patch(
            f"{API}/workspaces/{ws['ws_id']}/membership-policy",
            json={"allow_invitation_links": True, "max_members": 50},
            headers=auth_headers(ws["access_token"]),
        )
        assert resp.status_code == 200

    async def test_update_success_admin(self, client: AsyncClient):
        """200 — admin обновляет (через ws.settings.*)."""
        ws = await create_workspace_with_owner(client)
        admin = await register_and_login(client)
        await add_ws_member_with_role(
            client,
            ws_id=ws["ws_id"],
            owner_token=ws["access_token"],
            new_member_user_id=admin["user_id"],
            role_name="admin",
        )
        resp = await client.patch(
            f"{API}/workspaces/{ws['ws_id']}/membership-policy",
            json={"require_approval": True},
            headers=auth_headers(admin["access_token"]),
        )
        assert resp.status_code == 200

    async def test_update_no_auth(self, client: AsyncClient):
        """401 — без токена."""
        ws = await create_workspace_with_owner(client)
        resp = await client.patch(
            f"{API}/workspaces/{ws['ws_id']}/membership-policy",
            json={"allow_invitation_links": True},
        )
        assert resp.status_code == 401

    async def test_update_forbidden_manager(self, client: AsyncClient):
        """403 — manager (нет ws.settings.write)."""
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
            f"{API}/workspaces/{ws['ws_id']}/membership-policy",
            json={"allow_invitation_links": True},
            headers=auth_headers(manager["access_token"]),
        )
        assert resp.status_code == 403

    async def test_update_not_found(self, client: AsyncClient):
        """404 — несуществующий workspace."""
        user = await register_and_login(client)
        resp = await client.patch(
            f"{API}/workspaces/00000000-0000-0000-0000-000000000000/membership-policy",
            json={"allow_invitation_links": True},
            headers=auth_headers(user["access_token"]),
        )
        assert resp.status_code == 404

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
class TestUpdateWorkspaceSecurityPolicy:
    """PATCH /workspaces/{ws_id}/security-policy — Обновить политику безопасности (ws.settings.write)."""

    async def test_update_success_owner(self, client: AsyncClient):
        """200 — owner обновляет политику безопасности."""
        ws = await create_workspace_with_owner(client)
        resp = await client.patch(
            f"{API}/workspaces/{ws['ws_id']}/security-policy",
            json={"require_2fa": True, "session_timeout_minutes": 60},
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
            f"{API}/workspaces/{ws['ws_id']}/security-policy",
            json={"require_2fa": False},
            headers=auth_headers(admin["access_token"]),
        )
        assert resp.status_code == 200

    async def test_update_no_auth(self, client: AsyncClient):
        """401 — без токена."""
        ws = await create_workspace_with_owner(client)
        resp = await client.patch(
            f"{API}/workspaces/{ws['ws_id']}/security-policy",
            json={"require_2fa": True},
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
            f"{API}/workspaces/{ws['ws_id']}/security-policy",
            json={"require_2fa": True},
            headers=auth_headers(manager["access_token"]),
        )
        assert resp.status_code == 403

    async def test_update_forbidden_member(self, client: AsyncClient):
        """403 — member (нет ws.settings.write)."""
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
            f"{API}/workspaces/{ws['ws_id']}/security-policy",
            json={"require_2fa": True},
            headers=auth_headers(member["access_token"]),
        )
        assert resp.status_code == 403

    async def test_update_not_found(self, client: AsyncClient):
        """404 — несуществующий workspace."""
        user = await register_and_login(client)
        resp = await client.patch(
            f"{API}/workspaces/00000000-0000-0000-0000-000000000000/security-policy",
            json={"require_2fa": True},
            headers=auth_headers(user["access_token"]),
        )
        assert resp.status_code == 404

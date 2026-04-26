import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    create_workspace_with_owner,
    register_and_login,
    add_ws_member_with_role,
)


def _member_role_id(roles_resp):
    items = roles_resp.json()["items"]
    return next(r["id"] for r in items if r["name"] == "member")


@pytest.mark.e2e
class TestRevokeWorkspaceInvitation:
    """POST /workspaces/{ws_id}/invitations/{invitation_id}/revoke — Отозвать (members.invite)."""

    async def test_revoke_success_owner(self, client: AsyncClient):
        """200 — owner отзывает."""
        ws = await create_workspace_with_owner(client)
        roles_resp = await client.get(
            f"{API}/workspaces/{ws['ws_id']}/roles",
            params={"system_only": True},
            headers=auth_headers(ws["access_token"]),
        )
        role_id = _member_role_id(roles_resp)
        inv_resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/invitations/email",
            json={"email": "revoke@example.com", "role_id": role_id},
            headers=auth_headers(ws["access_token"]),
        )
        assert inv_resp.status_code == 201
        invitation_id = inv_resp.json()["data"]["id"]
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/invitations/{invitation_id}/revoke",
            headers=auth_headers(ws["access_token"]),
        )
        assert resp.status_code == 200

    async def test_revoke_success_admin(self, client: AsyncClient):
        """200 — admin отзывает."""
        ws = await create_workspace_with_owner(client)
        admin = await register_and_login(client)
        await add_ws_member_with_role(
            client,
            ws_id=ws["ws_id"],
            owner_token=ws["access_token"],
            new_member_user_id=admin["user_id"],
            role_name="admin",
        )
        roles_resp = await client.get(
            f"{API}/workspaces/{ws['ws_id']}/roles",
            params={"system_only": True},
            headers=auth_headers(ws["access_token"]),
        )
        role_id = _member_role_id(roles_resp)
        inv_resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/invitations/email",
            json={"email": "admin-revoke@example.com", "role_id": role_id},
            headers=auth_headers(ws["access_token"]),
        )
        invitation_id = inv_resp.json()["data"]["id"]
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/invitations/{invitation_id}/revoke",
            headers=auth_headers(admin["access_token"]),
        )
        assert resp.status_code == 200

    async def test_revoke_no_auth(self, client: AsyncClient):
        """401 — без токена."""
        ws = await create_workspace_with_owner(client)
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/invitations/00000000-0000-0000-0000-000000000000/revoke",
        )
        assert resp.status_code == 401

    async def test_revoke_forbidden_manager(self, client: AsyncClient):
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
            f"{API}/workspaces/{ws['ws_id']}/invitations/00000000-0000-0000-0000-000000000000/revoke",
            headers=auth_headers(manager["access_token"]),
        )
        assert resp.status_code == 403

    async def test_revoke_not_found(self, client: AsyncClient):
        """404 — приглашение не найдено."""
        ws = await create_workspace_with_owner(client)
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/invitations/00000000-0000-0000-0000-000000000000/revoke",
            headers=auth_headers(ws["access_token"]),
        )
        assert resp.status_code == 404

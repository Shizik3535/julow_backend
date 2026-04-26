import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    register_and_login,
    add_ws_member_with_role
)


def _member_role_id(roles_resp):
    items = roles_resp.json()["items"]
    return next(r["id"] for r in items if r["name"] == "member")


@pytest.mark.e2e
class TestSendBulkWorkspaceInvitations:
    """POST /workspaces/{ws_id}/invitations/bulk — Массовая отправка (members.invite)."""

    async def test_bulk_success_owner(self, client: AsyncClient, workspace_owner):
        """201 — owner массово отправляет."""
        ws = workspace_owner
        roles_resp = await client.get(
            f"{API}/workspaces/{ws['ws_id']}/roles",
            params={"system_only": True},
            headers=auth_headers(ws["access_token"])
        )
        role_id = _member_role_id(roles_resp)
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/invitations/bulk",
            json={"emails": ["bulk1@example.com", "bulk2@example.com"], "role_id": role_id},
            headers=auth_headers(ws["access_token"])
        )
        assert resp.status_code == 201

    async def test_bulk_success_admin(self, client: AsyncClient, workspace_owner):
        """201 — admin массово отправляет."""
        ws = workspace_owner
        admin = await register_and_login(client)
        await add_ws_member_with_role(
            client,
            ws_id=ws["ws_id"],
            owner_token=ws["access_token"],
            new_member_user_id=admin["user_id"],
            role_name="admin"
        )
        roles_resp = await client.get(
            f"{API}/workspaces/{ws['ws_id']}/roles",
            params={"system_only": True},
            headers=auth_headers(ws["access_token"])
        )
        role_id = _member_role_id(roles_resp)
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/invitations/bulk",
            json={"emails": ["admin-bulk@example.com"], "role_id": role_id},
            headers=auth_headers(admin["access_token"])
        )
        assert resp.status_code == 201

    async def test_bulk_no_auth(self, client: AsyncClient, workspace_owner):
        """401 — без токена."""
        ws = workspace_owner
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/invitations/bulk",
            json={"emails": ["noauth@example.com"], "role_id": "some-role"}
        )
        assert resp.status_code == 401

    async def test_bulk_forbidden_manager(self, client: AsyncClient, workspace_owner):
        """403 — manager."""
        ws = workspace_owner
        manager = await register_and_login(client)
        await add_ws_member_with_role(
            client,
            ws_id=ws["ws_id"],
            owner_token=ws["access_token"],
            new_member_user_id=manager["user_id"],
            role_name="manager"
        )
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/invitations/bulk",
            json={"emails": ["mgr@example.com"], "role_id": "some-role"},
            headers=auth_headers(manager["access_token"])
        )
        assert resp.status_code == 403

    async def test_bulk_not_found(self, client: AsyncClient):
        """404 — несуществующий workspace."""
        user = await register_and_login(client)
        resp = await client.post(
            f"{API}/workspaces/00000000-0000-0000-0000-000000000000/invitations/bulk",
            json={"emails": ["ghost@example.com"], "role_id": "some-role"},
            headers=auth_headers(user["access_token"])
        )
        assert resp.status_code == 404

    async def test_bulk_validation_empty_emails(self, client: AsyncClient, workspace_owner):
        """422 — пустой список emails."""
        ws = workspace_owner
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/invitations/bulk",
            json={"emails": [], "role_id": "some-role"},
            headers=auth_headers(ws["access_token"])
        )
        assert resp.status_code == 422

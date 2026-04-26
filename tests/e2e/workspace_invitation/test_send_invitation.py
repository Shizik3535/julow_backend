import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    create_workspace_with_owner,
    register_and_login,
    add_ws_member_with_role,
)


def _member_role_id(ws, roles_resp):
    items = roles_resp.json()["items"]
    return next(r["id"] for r in items if r["name"] == "member")


@pytest.mark.e2e
class TestSendWorkspaceInvitation:
    """POST /workspaces/{ws_id}/invitations/email — Отправить приглашение (members.invite)."""

    async def test_send_invitation_success_owner(self, client: AsyncClient):
        """201 — owner отправляет приглашение."""
        ws = await create_workspace_with_owner(client)
        roles_resp = await client.get(
            f"{API}/workspaces/{ws['ws_id']}/roles",
            params={"system_only": True},
            headers=auth_headers(ws["access_token"]),
        )
        role_id = _member_role_id(ws, roles_resp)
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/invitations/email",
            json={"email": "invited@example.com", "role_id": role_id},
            headers=auth_headers(ws["access_token"]),
        )
        assert resp.status_code == 201

    async def test_send_invitation_success_admin(self, client: AsyncClient):
        """201 — admin отправляет."""
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
        role_id = _member_role_id(ws, roles_resp)
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/invitations/email",
            json={"email": "admin-invited@example.com", "role_id": role_id},
            headers=auth_headers(admin["access_token"]),
        )
        assert resp.status_code == 201

    async def test_send_invitation_no_auth(self, client: AsyncClient):
        """401 — без токена."""
        ws = await create_workspace_with_owner(client)
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/invitations/email",
            json={"email": "noauth@example.com", "role_id": "some-role"},
        )
        assert resp.status_code == 401

    async def test_send_invitation_forbidden_manager(self, client: AsyncClient):
        """403 — manager (нет members.invite)."""
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
            f"{API}/workspaces/{ws['ws_id']}/invitations/email",
            json={"email": "mgr-inv@example.com", "role_id": "some-role"},
            headers=auth_headers(manager["access_token"]),
        )
        assert resp.status_code == 403

    async def test_send_invitation_forbidden_member(self, client: AsyncClient):
        """403 — member."""
        ws = await create_workspace_with_owner(client)
        member = await register_and_login(client)
        await add_ws_member_with_role(
            client,
            ws_id=ws["ws_id"],
            owner_token=ws["access_token"],
            new_member_user_id=member["user_id"],
            role_name="member",
        )
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/invitations/email",
            json={"email": "mem-inv@example.com", "role_id": "some-role"},
            headers=auth_headers(member["access_token"]),
        )
        assert resp.status_code == 403

    async def test_send_invitation_not_found(self, client: AsyncClient):
        """404 — несуществующий workspace."""
        user = await register_and_login(client)
        resp = await client.post(
            f"{API}/workspaces/00000000-0000-0000-0000-000000000000/invitations/email",
            json={"email": "ghost@example.com", "role_id": "some-role"},
            headers=auth_headers(user["access_token"]),
        )
        assert resp.status_code == 404

    async def test_send_invitation_conflict_duplicate(self, client: AsyncClient):
        """409 — приглашение уже отправлено этому email."""
        ws = await create_workspace_with_owner(client)
        roles_resp = await client.get(
            f"{API}/workspaces/{ws['ws_id']}/roles",
            params={"system_only": True},
            headers=auth_headers(ws["access_token"]),
        )
        role_id = _member_role_id(ws, roles_resp)
        await client.post(
            f"{API}/workspaces/{ws['ws_id']}/invitations/email",
            json={"email": "dup@example.com", "role_id": role_id},
            headers=auth_headers(ws["access_token"]),
        )
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/invitations/email",
            json={"email": "dup@example.com", "role_id": role_id},
            headers=auth_headers(ws["access_token"]),
        )
        assert resp.status_code == 409

    async def test_send_invitation_validation_invalid_email(self, client: AsyncClient):
        """422 — невалидный email."""
        ws = await create_workspace_with_owner(client)
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/invitations/email",
            json={"email": "not-an-email", "role_id": "some-role"},
            headers=auth_headers(ws["access_token"]),
        )
        assert resp.status_code == 422

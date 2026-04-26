import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    create_workspace_with_owner,
    register_and_login,
)


def _member_role_id(roles_resp):
    items = roles_resp.json()["items"]
    return next(r["id"] for r in items if r["name"] == "member")


@pytest.mark.e2e
class TestDeclineWorkspaceInvitation:
    """POST /workspaces/invitations/{invitation_id}/decline — Отклонить (без проверки)."""

    async def test_decline_success(self, client: AsyncClient):
        """200 — отклонение приглашения."""
        ws = await create_workspace_with_owner(client)
        roles_resp = await client.get(
            f"{API}/workspaces/{ws['ws_id']}/roles",
            params={"system_only": True},
            headers=auth_headers(ws["access_token"]),
        )
        role_id = _member_role_id(roles_resp)
        invitee = await register_and_login(client)
        inv_resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/invitations/email",
            json={"email": invitee["email"], "role_id": role_id},
            headers=auth_headers(ws["access_token"]),
        )
        assert inv_resp.status_code == 201
        invitation_id = inv_resp.json()["data"]["id"]
        resp = await client.post(
            f"{API}/workspaces/invitations/{invitation_id}/decline",
            headers=auth_headers(invitee["access_token"]),
        )
        assert resp.status_code == 200

    async def test_decline_not_found(self, client: AsyncClient):
        """404 — приглашение не найдено."""
        user = await register_and_login(client)
        resp = await client.post(
            f"{API}/workspaces/invitations/00000000-0000-0000-0000-000000000000/decline",
            headers=auth_headers(user["access_token"]),
        )
        assert resp.status_code == 404

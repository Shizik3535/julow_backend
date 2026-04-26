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
class TestWorkspaceInvitationFlow:
    """Сценарий: send_invitation → get_invitations → generate_link → get_by_token (без auth) → accept → decline → revoke."""

    async def test_full_invitation_flow(self, client: AsyncClient):
        ws = await create_workspace_with_owner(client)
        h = auth_headers(ws["access_token"])
        ws_id = ws["ws_id"]

        # 1. Get member role
        roles_resp = await client.get(
            f"{API}/workspaces/{ws_id}/roles",
            params={"system_only": True},
            headers=h,
        )
        role_id = _member_role_id(roles_resp)

        # 2. Send invitation
        invitee = await register_and_login(client)
        inv_resp = await client.post(
            f"{API}/workspaces/{ws_id}/invitations/email",
            json={"email": invitee["email"], "role_id": role_id},
            headers=h,
        )
        assert inv_resp.status_code == 201
        invitation_id = inv_resp.json()["data"]["id"]

        # 3. Get invitations
        resp = await client.get(f"{API}/workspaces/{ws_id}/invitations", headers=h)
        assert resp.status_code == 200

        # 4. Generate link
        link_resp = await client.post(
            f"{API}/workspaces/{ws_id}/invitations/link",
            json={"role_id": role_id},
            headers=h,
        )
        assert link_resp.status_code == 201
        token = link_resp.json()["data"]["link"]["value"]

        # 5. Get by token (без auth)
        resp = await client.get(f"{API}/workspaces/invitations/token/{token}")
        assert resp.status_code == 200

        # 6. Decline invitation
        resp = await client.post(
            f"{API}/workspaces/invitations/{invitation_id}/decline",
            headers=auth_headers(invitee["access_token"]),
        )
        assert resp.status_code == 200

        # 7. Send another invitation for revoke test
        inv_resp2 = await client.post(
            f"{API}/workspaces/{ws_id}/invitations/email",
            json={"email": "revoke-test@example.com", "role_id": role_id},
            headers=h,
        )
        assert inv_resp2.status_code == 201
        inv2_id = inv_resp2.json()["data"]["id"]

        # 8. Revoke
        resp = await client.post(
            f"{API}/workspaces/{ws_id}/invitations/{inv2_id}/revoke",
            headers=h,
        )
        assert resp.status_code == 200

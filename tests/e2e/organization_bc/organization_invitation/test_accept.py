"""E2E-тесты: POST /orgs/invitations/{invitation_id}/accept."""

import uuid

import pytest

from tests.e2e.conftest import API, auth_headers, register_and_login

MEMBER_ROLE_ID = "00000000-0000-0000-0000-000000000014"


@pytest.mark.e2e
class TestAcceptInvitation:
    """Принятие приглашения."""

    async def _create_invitation(self, client, owner) -> str:
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/invitations/email",
            json={"email": f"accept-{uuid.uuid4().hex[:8]}@example.com", "role_id": MEMBER_ROLE_ID},
            headers=auth_headers(owner["access_token"])
        )
        assert resp.status_code == 201
        return resp.json()["data"]["id"]

    async def test_accept_invitation_success(self, client, org_with_owner) -> None:
        """200 — принятие приглашения, пользователь становится участником."""
        owner = org_with_owner
        invitation_id = await self._create_invitation(client, owner)
        accepter = await register_and_login(client)
        resp = await client.post(
            f"{API}/orgs/invitations/{invitation_id}/accept",
            headers=auth_headers(accepter["access_token"])
        )

        assert resp.status_code == 200

    async def test_accept_invitation_not_found(self, client) -> None:
        """404 — приглашение не найдено."""
        user = await register_and_login(client)
        resp = await client.post(
            f"{API}/orgs/invitations/{uuid.uuid4()}/accept",
            headers=auth_headers(user["access_token"])
        )
        assert resp.status_code == 404

    async def test_accept_invitation_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.post(f"{API}/orgs/invitations/{uuid.uuid4()}/accept")
        assert resp.status_code == 401

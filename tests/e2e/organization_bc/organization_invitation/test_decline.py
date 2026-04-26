"""E2E-тесты: POST /orgs/invitations/{invitation_id}/decline."""

import uuid

import pytest

from tests.e2e.conftest import API, auth_headers, register_and_login

MEMBER_ROLE_ID = "00000000-0000-0000-0000-000000000014"


@pytest.mark.e2e
class TestDeclineInvitation:
    """Отклонение приглашения."""

    async def _create_invitation(self, client, owner, email: str) -> str:
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/invitations/email",
            json={"email": email, "role_id": MEMBER_ROLE_ID},
            headers=auth_headers(owner["access_token"])
        )
        assert resp.status_code == 201
        return resp.json()["data"]["id"]

    async def test_decline_invitation_success(self, client, org_with_owner) -> None:
        """200 — отклонение приглашения."""
        owner = org_with_owner
        invitee_email = f"decline-{uuid.uuid4().hex[:8]}@example.com"
        invitation_id = await self._create_invitation(client, owner, invitee_email)
        decliner = await register_and_login(client, email=invitee_email)
        resp = await client.post(
            f"{API}/orgs/invitations/{invitation_id}/decline",
            headers=auth_headers(decliner["access_token"])
        )

        assert resp.status_code == 200

    async def test_decline_invitation_not_found(self, client) -> None:
        """404 — приглашение не найдено."""
        user = await register_and_login(client)
        resp = await client.post(
            f"{API}/orgs/invitations/{uuid.uuid4()}/decline",
            headers=auth_headers(user["access_token"])
        )
        assert resp.status_code == 404

    async def test_decline_invitation_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.post(f"{API}/orgs/invitations/{uuid.uuid4()}/decline")
        assert resp.status_code == 401

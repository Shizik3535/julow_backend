"""E2E-тесты: POST /orgs/{org_id}/invitations/email."""

import uuid

import pytest

from tests.e2e.conftest import API, auth_headers, register_and_login

MEMBER_ROLE_ID = "00000000-0000-0000-0000-000000000014"


@pytest.mark.e2e
class TestSendInvitation:
    """Отправка email-приглашения."""

    async def test_send_invitation_success(self, client, org_with_owner) -> None:
        """201 — отправка email-приглашения."""
        owner = org_with_owner
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/invitations/email",
            json={"email": f"invite-{uuid.uuid4().hex[:8]}@example.com", "role_id": MEMBER_ROLE_ID},
            headers=auth_headers(owner["access_token"])
        )

        assert resp.status_code == 201
        data = resp.json()["data"]
        assert data["id"]

    async def test_send_invitation_conflict(self, client, org_with_owner) -> None:
        """409 — повторное приглашение на тот же email."""
        owner = org_with_owner
        email = f"dup-{uuid.uuid4().hex[:8]}@example.com"
        await client.post(
            f"{API}/orgs/{owner['org_id']}/invitations/email",
            json={"email": email, "role_id": MEMBER_ROLE_ID},
            headers=auth_headers(owner["access_token"])
        )
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/invitations/email",
            json={"email": email, "role_id": MEMBER_ROLE_ID},
            headers=auth_headers(owner["access_token"])
        )
        assert resp.status_code == 409

    async def test_send_invitation_forbidden(self, client, org_with_owner) -> None:
        """403 — не-владелец не может отправить приглашение."""
        owner = org_with_owner
        other = await register_and_login(client)
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/invitations/email",
            json={"email": f"hax-{uuid.uuid4().hex[:8]}@example.com", "role_id": MEMBER_ROLE_ID},
            headers=auth_headers(other["access_token"])
        )
        assert resp.status_code == 403

    async def test_send_invitation_not_found(self, client, org_with_owner) -> None:
        """404 — организация не найдена."""
        owner = org_with_owner
        resp = await client.post(
            f"{API}/orgs/{uuid.uuid4()}/invitations/email",
            json={"email": f"ghost-{uuid.uuid4().hex[:8]}@example.com", "role_id": MEMBER_ROLE_ID},
            headers=auth_headers(owner["access_token"])
        )
        assert resp.status_code == 404

    async def test_send_invitation_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.post(
            f"{API}/orgs/{uuid.uuid4()}/invitations/email",
            json={"email": "noauth@example.com", "role_id": MEMBER_ROLE_ID}
        )
        assert resp.status_code == 401

    async def test_send_invitation_validation(self, client, org_with_owner) -> None:
        """422 — невалидный email."""
        owner = org_with_owner
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/invitations/email",
            json={"email": "not-an-email", "role_id": MEMBER_ROLE_ID},
            headers=auth_headers(owner["access_token"])
        )
        assert resp.status_code == 422

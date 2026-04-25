"""E2E-тесты: POST /orgs/{org_id}/invitations/bulk."""

import uuid

import pytest

from tests.e2e.conftest import API, auth_headers, create_org_with_owner, register_and_login

MEMBER_ROLE_ID = "00000000-0000-0000-0000-000000000014"


@pytest.mark.e2e
class TestSendBulkInvitations:
    """Массовая отправка приглашений."""

    async def test_send_bulk_invitations_success(self, client) -> None:
        """201 — массовая отправка на несколько email."""
        owner = await create_org_with_owner(client)
        emails = [
            f"bulk1-{uuid.uuid4().hex[:8]}@example.com",
            f"bulk2-{uuid.uuid4().hex[:8]}@example.com",
        ]
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/invitations/bulk",
            json={"emails": emails, "role_id": MEMBER_ROLE_ID},
            headers=auth_headers(owner["access_token"]),
        )

        assert resp.status_code == 201
        data = resp.json()["data"]
        assert isinstance(data, list)

    async def test_send_bulk_invitations_forbidden(self, client) -> None:
        """403 — не-владелец не может отправить приглашения."""
        owner = await create_org_with_owner(client)
        other = await register_and_login(client)
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/invitations/bulk",
            json={"emails": ["a@example.com"], "role_id": MEMBER_ROLE_ID},
            headers=auth_headers(other["access_token"]),
        )
        assert resp.status_code == 403

    async def test_send_bulk_invitations_not_found(self, client) -> None:
        """404 — организация не найдена."""
        owner = await create_org_with_owner(client)
        resp = await client.post(
            f"{API}/orgs/{uuid.uuid4()}/invitations/bulk",
            json={"emails": ["a@example.com"], "role_id": MEMBER_ROLE_ID},
            headers=auth_headers(owner["access_token"]),
        )
        assert resp.status_code == 404

    async def test_send_bulk_invitations_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.post(
            f"{API}/orgs/{uuid.uuid4()}/invitations/bulk",
            json={"emails": ["a@example.com"], "role_id": MEMBER_ROLE_ID},
        )
        assert resp.status_code == 401

    async def test_send_bulk_invitations_validation(self, client) -> None:
        """422 — пустой список emails."""
        owner = await create_org_with_owner(client)
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/invitations/bulk",
            json={"emails": [], "role_id": MEMBER_ROLE_ID},
            headers=auth_headers(owner["access_token"]),
        )
        assert resp.status_code == 422

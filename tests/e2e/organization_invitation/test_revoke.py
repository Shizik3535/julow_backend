"""E2E-тесты: POST /orgs/{org_id}/invitations/{invitation_id}/revoke."""

import uuid

import pytest

from tests.e2e.conftest import API, auth_headers, create_org_with_owner, register_and_login

MEMBER_ROLE_ID = "00000000-0000-0000-0000-000000000014"


@pytest.mark.e2e
class TestRevokeInvitation:
    """Отзыв приглашения."""

    async def _create_invitation(self, client, owner) -> str:
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/invitations/email",
            json={"email": f"revoke-{uuid.uuid4().hex[:8]}@example.com", "role_id": MEMBER_ROLE_ID},
            headers=auth_headers(owner["access_token"]),
        )
        assert resp.status_code == 201
        return resp.json()["data"]["id"]

    async def test_revoke_invitation_success(self, client) -> None:
        """200 — отзыв приглашения."""
        owner = await create_org_with_owner(client)
        invitation_id = await self._create_invitation(client, owner)
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/invitations/{invitation_id}/revoke",
            headers=auth_headers(owner["access_token"]),
        )

        assert resp.status_code == 200

    async def test_revoke_invitation_forbidden(self, client) -> None:
        """403 — не-владелец не может отозвать."""
        owner = await create_org_with_owner(client)
        invitation_id = await self._create_invitation(client, owner)
        other = await register_and_login(client)
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/invitations/{invitation_id}/revoke",
            headers=auth_headers(other["access_token"]),
        )
        assert resp.status_code == 403

    async def test_revoke_invitation_not_found(self, client) -> None:
        """404 — приглашение не найдено."""
        owner = await create_org_with_owner(client)
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/invitations/{uuid.uuid4()}/revoke",
            headers=auth_headers(owner["access_token"]),
        )
        assert resp.status_code == 404

    async def test_revoke_invitation_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.post(
            f"{API}/orgs/{uuid.uuid4()}/invitations/{uuid.uuid4()}/revoke",
        )
        assert resp.status_code == 401

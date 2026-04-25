"""E2E-тесты: POST /orgs/{org_id}/invitations/link."""

import uuid

import pytest

from tests.e2e.conftest import API, auth_headers, create_org_with_owner, register_and_login

MEMBER_ROLE_ID = "00000000-0000-0000-0000-000000000014"


@pytest.mark.e2e
class TestGenerateInvitationLink:
    """Генерация ссылки-приглашения."""

    async def test_generate_link_success(self, client) -> None:
        """201 — генерация ссылки с ограничениями."""
        owner = await create_org_with_owner(client)
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/invitations/link",
            json={"role_id": MEMBER_ROLE_ID, "max_uses": 10, "expires_in_hours": 48},
            headers=auth_headers(owner["access_token"]),
        )

        assert resp.status_code == 201
        data = resp.json()["data"]
        assert data["id"]
        assert data.get("token") or data.get("link")

    async def test_generate_link_minimal(self, client) -> None:
        """201 — генерация ссылки без ограничений."""
        owner = await create_org_with_owner(client)
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/invitations/link",
            json={"role_id": MEMBER_ROLE_ID},
            headers=auth_headers(owner["access_token"]),
        )

        assert resp.status_code == 201

    async def test_generate_link_forbidden(self, client) -> None:
        """403 — не-владелец не может генерировать ссылку."""
        owner = await create_org_with_owner(client)
        other = await register_and_login(client)
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/invitations/link",
            json={"role_id": MEMBER_ROLE_ID},
            headers=auth_headers(other["access_token"]),
        )
        assert resp.status_code == 403

    async def test_generate_link_not_found(self, client) -> None:
        """404 — организация не найдена."""
        owner = await create_org_with_owner(client)
        resp = await client.post(
            f"{API}/orgs/{uuid.uuid4()}/invitations/link",
            json={"role_id": MEMBER_ROLE_ID},
            headers=auth_headers(owner["access_token"]),
        )
        assert resp.status_code == 404

    async def test_generate_link_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.post(f"{API}/orgs/{uuid.uuid4()}/invitations/link", json={"role_id": MEMBER_ROLE_ID})
        assert resp.status_code == 401

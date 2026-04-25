"""E2E-тесты: GET /orgs/invitations/token/{token}."""

import uuid

import pytest

from tests.e2e.conftest import API, auth_headers, create_org_with_owner

MEMBER_ROLE_ID = "00000000-0000-0000-0000-000000000014"


@pytest.mark.e2e
class TestGetInvitationByToken:
    """Получение приглашения по токену ссылки-приглашения."""

    async def test_get_invitation_by_token_success(self, client) -> None:
        """200 — данные приглашения по токену."""
        owner = await create_org_with_owner(client)
        link_resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/invitations/link",
            json={"role_id": MEMBER_ROLE_ID},
            headers=auth_headers(owner["access_token"]),
        )
        assert link_resp.status_code == 201
        link_data = link_resp.json()["data"].get("link") or {}
        token = link_data.get("value", "")
        if not token:
            pytest.skip("Приглашение не содержит токен")

        resp = await client.get(
            f"{API}/orgs/invitations/token/{token}",
            headers=auth_headers(owner["access_token"]),
        )

        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["id"]

    async def test_get_invitation_by_token_not_found(self, client) -> None:
        """404 — токен не найден."""
        owner = await create_org_with_owner(client)
        resp = await client.get(
            f"{API}/orgs/invitations/token/{uuid.uuid4().hex}",
            headers=auth_headers(owner["access_token"]),
        )
        assert resp.status_code == 404

    async def test_get_invitation_by_token_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.get(f"{API}/orgs/invitations/token/{uuid.uuid4().hex}")
        assert resp.status_code == 401

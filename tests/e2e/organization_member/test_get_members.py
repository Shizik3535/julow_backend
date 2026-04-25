"""E2E-тесты: GET /orgs/{org_id}/members."""

import uuid

import pytest

from tests.e2e.conftest import API, auth_headers, create_org_with_owner


@pytest.mark.e2e
class TestGetMembers:
    """Список участников организации."""

    async def test_get_members_success(self, client) -> None:
        """200 — список участников (владелец видит себя)."""
        owner = await create_org_with_owner(client)
        resp = await client.get(
            f"{API}/orgs/{owner['org_id']}/members",
            headers=auth_headers(owner["access_token"]),
        )

        assert resp.status_code == 200
        data = resp.json()["data"]
        assert isinstance(data, list)
        member_ids = [m["user_id"] for m in data]
        assert owner["user_id"] in member_ids

    async def test_get_members_not_found(self, client) -> None:
        """404 — организация не найдена."""
        owner = await create_org_with_owner(client)
        resp = await client.get(
            f"{API}/orgs/{uuid.uuid4()}/members",
            headers=auth_headers(owner["access_token"]),
        )
        assert resp.status_code == 404

    async def test_get_members_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.get(f"{API}/orgs/{uuid.uuid4()}/members")
        assert resp.status_code == 401

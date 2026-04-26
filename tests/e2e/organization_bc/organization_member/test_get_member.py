"""E2E-тесты: GET /orgs/{org_id}/members/{user_id}."""

import uuid

import pytest

from tests.e2e.conftest import API, auth_headers


@pytest.mark.e2e
class TestGetMember:
    """Получение данных конкретного участника."""

    async def test_get_member_success(self, client, org_with_owner) -> None:
        """200 — данные владельца как участника."""
        owner = org_with_owner
        resp = await client.get(
            f"{API}/orgs/{owner['org_id']}/members/{owner['user_id']}",
            headers=auth_headers(owner["access_token"])
        )

        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["user_id"] == owner["user_id"]

    async def test_get_member_not_found(self, client, org_with_owner) -> None:
        """404 — участник не найден в организации."""
        owner = org_with_owner
        resp = await client.get(
            f"{API}/orgs/{owner['org_id']}/members/{uuid.uuid4()}",
            headers=auth_headers(owner["access_token"])
        )
        assert resp.status_code == 404

    async def test_get_member_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.get(f"{API}/orgs/{uuid.uuid4()}/members/{uuid.uuid4()}")
        assert resp.status_code == 401

"""E2E-тесты: GET /orgs/{org_id}."""

import uuid

import pytest

from tests.e2e.conftest import API, auth_headers


@pytest.mark.e2e
class TestGetOrganization:
    """Получение организации по ID."""

    async def test_get_organization_success(self, client, org_with_owner) -> None:
        """200 — данные существующей организации."""
        owner = org_with_owner
        resp = await client.get(
            f"{API}/orgs/{owner['org_id']}",
            headers=auth_headers(owner["access_token"])
        )

        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["id"] == owner["org_id"]
        assert data["name"] == owner["org_name"]
        assert data["status"] == "active"

    async def test_get_organization_not_found(self, client, org_with_owner) -> None:
        """404 — организация не найдена."""
        owner = org_with_owner
        resp = await client.get(
            f"{API}/orgs/{uuid.uuid4()}",
            headers=auth_headers(owner["access_token"])
        )
        assert resp.status_code == 404

    async def test_get_organization_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.get(f"{API}/orgs/{uuid.uuid4()}")
        assert resp.status_code == 401

"""E2E-тесты: POST /orgs."""

import pytest

from tests.e2e.conftest import API, auth_headers, register_and_login


@pytest.mark.e2e
class TestCreateOrganization:
    """Создание организации."""

    async def test_create_organization_success(self, client) -> None:
        """201 — организация создана, текущий пользователь — владелец."""
        user = await register_and_login(client)
        resp = await client.post(
            f"{API}/orgs/",
            json={"name": "Test Org"},
            headers=auth_headers(user["access_token"]),
        )

        assert resp.status_code == 201
        data = resp.json()["data"]
        assert data["id"]
        assert data["name"] == "Test Org"
        assert data["status"] == "active"
        assert user["user_id"] in data["owner_ids"]

    async def test_create_organization_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.post(f"{API}/orgs/", json={"name": "NoAuth Org"})
        assert resp.status_code == 401

    async def test_create_organization_empty_name(self, client) -> None:
        """422 — пустое название организации."""
        user = await register_and_login(client)
        resp = await client.post(
            f"{API}/orgs/",
            json={"name": ""},
            headers=auth_headers(user["access_token"]),
        )
        assert resp.status_code == 422

    async def test_create_organization_missing_body(self, client) -> None:
        """422 — отсутствует тело запроса."""
        user = await register_and_login(client)
        resp = await client.post(
            f"{API}/orgs/",
            json={},
            headers=auth_headers(user["access_token"]),
        )
        assert resp.status_code == 422

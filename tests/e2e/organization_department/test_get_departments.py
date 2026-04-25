"""E2E-тесты: GET /orgs/{org_id}/departments."""

import uuid

import pytest

from tests.e2e.conftest import API, auth_headers, create_org_with_owner


@pytest.mark.e2e
class TestGetDepartments:
    """Список подразделений организации."""

    async def test_get_departments_success(self, client) -> None:
        """200 — список подразделений (пустой изначально)."""
        owner = await create_org_with_owner(client)
        resp = await client.get(
            f"{API}/orgs/{owner['org_id']}/departments",
            headers=auth_headers(owner["access_token"]),
        )

        assert resp.status_code == 200
        data = resp.json()["data"]
        assert isinstance(data, list)

    async def test_get_departments_not_found(self, client) -> None:
        """404 — организация не найдена."""
        owner = await create_org_with_owner(client)
        resp = await client.get(
            f"{API}/orgs/{uuid.uuid4()}/departments",
            headers=auth_headers(owner["access_token"]),
        )
        assert resp.status_code == 404

    async def test_get_departments_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.get(f"{API}/orgs/{uuid.uuid4()}/departments")
        assert resp.status_code == 401

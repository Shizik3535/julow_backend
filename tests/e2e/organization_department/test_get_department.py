"""E2E-тесты: GET /orgs/{org_id}/departments/{department_id}."""

import uuid

import pytest

from tests.e2e.conftest import API, auth_headers, create_org_with_owner


@pytest.mark.e2e
class TestGetDepartment:
    """Получение подразделения по ID."""

    async def _create_department(self, client, owner) -> str:
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/departments",
            json={"name": "Test Department"},
            headers=auth_headers(owner["access_token"]),
        )
        assert resp.status_code == 201
        return resp.json()["data"]["id"]

    async def test_get_department_success(self, client) -> None:
        """200 — данные созданного подразделения."""
        owner = await create_org_with_owner(client)
        dept_id = await self._create_department(client, owner)
        resp = await client.get(
            f"{API}/orgs/{owner['org_id']}/departments/{dept_id}",
            headers=auth_headers(owner["access_token"]),
        )

        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["id"] == dept_id
        assert data["name"] == "Test Department"

    async def test_get_department_not_found(self, client) -> None:
        """404 — подразделение не найдено."""
        owner = await create_org_with_owner(client)
        resp = await client.get(
            f"{API}/orgs/{owner['org_id']}/departments/{uuid.uuid4()}",
            headers=auth_headers(owner["access_token"]),
        )
        assert resp.status_code == 404

    async def test_get_department_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.get(f"{API}/orgs/{uuid.uuid4()}/departments/{uuid.uuid4()}")
        assert resp.status_code == 401

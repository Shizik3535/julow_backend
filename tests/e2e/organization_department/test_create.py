"""E2E-тесты: POST /orgs/{org_id}/departments."""

import uuid

import pytest

from tests.e2e.conftest import API, auth_headers, create_org_with_owner, register_and_login


@pytest.mark.e2e
class TestCreateDepartment:
    """Создание подразделения."""

    async def test_create_department_success(self, client) -> None:
        """201 — создание подразделения."""
        owner = await create_org_with_owner(client)
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/departments",
            json={"name": "Engineering"},
            headers=auth_headers(owner["access_token"]),
        )

        assert resp.status_code == 201
        data = resp.json()["data"]
        assert data["id"]
        assert data["name"] == "Engineering"

    async def test_create_department_forbidden(self, client) -> None:
        """403 — не-владелец не может создать подразделение."""
        owner = await create_org_with_owner(client)
        other = await register_and_login(client)
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/departments",
            json={"name": "Hacked Dept"},
            headers=auth_headers(other["access_token"]),
        )
        assert resp.status_code == 403

    async def test_create_department_not_found(self, client) -> None:
        """404 — организация не найдена."""
        owner = await create_org_with_owner(client)
        resp = await client.post(
            f"{API}/orgs/{uuid.uuid4()}/departments",
            json={"name": "Ghost Dept"},
            headers=auth_headers(owner["access_token"]),
        )
        assert resp.status_code == 404

    async def test_create_department_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.post(
            f"{API}/orgs/{uuid.uuid4()}/departments",
            json={"name": "NoAuth Dept"},
        )
        assert resp.status_code == 401

    async def test_create_department_validation(self, client) -> None:
        """422 — отсутствует name."""
        owner = await create_org_with_owner(client)
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/departments",
            json={},
            headers=auth_headers(owner["access_token"]),
        )
        assert resp.status_code == 422

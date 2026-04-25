"""E2E-тесты: POST /orgs/{org_id}/roles."""

import uuid

import pytest

from tests.e2e.conftest import API, auth_headers, create_org_with_owner, register_and_login


@pytest.mark.e2e
class TestCreateRole:
    """Создание кастомной роли."""

    async def test_create_role_success(self, client) -> None:
        """201 — создание кастомной роли с permissions."""
        owner = await create_org_with_owner(client)
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/roles",
            json={
                "name": "Custom Role",
                "permissions": ["members:read"],
                "scope": "org",
                "description": "Test custom role",
            },
            headers=auth_headers(owner["access_token"]),
        )

        assert resp.status_code == 201
        data = resp.json()["data"]
        assert data["name"] == "Custom Role"
        assert data["is_system"] is False

    async def test_create_role_forbidden(self, client) -> None:
        """403 — не-владелец не может создать роль."""
        owner = await create_org_with_owner(client)
        other = await register_and_login(client)
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/roles",
            json={
                "name": "Hacked Role",
                "permissions": ["members:read"],
                "scope": "org",
            },
            headers=auth_headers(other["access_token"]),
        )
        assert resp.status_code == 403

    async def test_create_role_not_found(self, client) -> None:
        """404 — организация не найдена."""
        owner = await create_org_with_owner(client)
        resp = await client.post(
            f"{API}/orgs/{uuid.uuid4()}/roles",
            json={
                "name": "Ghost Role",
                "permissions": ["members:read"],
                "scope": "org",
            },
            headers=auth_headers(owner["access_token"]),
        )
        assert resp.status_code == 404

    async def test_create_role_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.post(
            f"{API}/orgs/{uuid.uuid4()}/roles",
            json={"name": "NoAuth Role", "permissions": ["members:read"], "scope": "org"},
        )
        assert resp.status_code == 401

    async def test_create_role_validation(self, client) -> None:
        """422 — отсутствует name."""
        owner = await create_org_with_owner(client)
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/roles",
            json={"permissions": ["members:read"], "scope": "org"},
            headers=auth_headers(owner["access_token"]),
        )
        assert resp.status_code == 422

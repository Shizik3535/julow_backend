"""E2E-тесты: GET /orgs/{org_id}/roles."""

import uuid

import pytest

from tests.e2e.conftest import API, auth_headers, create_org_with_owner


@pytest.mark.e2e
class TestGetRoles:
    """Список ролей организации."""

    async def test_get_roles_success(self, client) -> None:
        """200 — список ролей (включая системные)."""
        owner = await create_org_with_owner(client)
        resp = await client.get(
            f"{API}/orgs/{owner['org_id']}/roles",
            headers=auth_headers(owner["access_token"]),
        )

        assert resp.status_code == 200
        data = resp.json()["data"]
        assert isinstance(data, list)
        assert len(data) > 0

    async def test_get_roles_system_only(self, client) -> None:
        """200 — фильтр system_only=true."""
        owner = await create_org_with_owner(client)
        resp = await client.get(
            f"{API}/orgs/{owner['org_id']}/roles?system_only=true",
            headers=auth_headers(owner["access_token"]),
        )

        assert resp.status_code == 200
        data = resp.json()["data"]
        assert isinstance(data, list)

    async def test_get_roles_not_found(self, client) -> None:
        """404 — организация не найдена."""
        owner = await create_org_with_owner(client)
        resp = await client.get(
            f"{API}/orgs/{uuid.uuid4()}/roles",
            headers=auth_headers(owner["access_token"]),
        )
        assert resp.status_code == 404

    async def test_get_roles_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.get(f"{API}/orgs/{uuid.uuid4()}/roles")
        assert resp.status_code == 401

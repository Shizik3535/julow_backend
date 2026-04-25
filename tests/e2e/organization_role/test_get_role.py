"""E2E-тесты: GET /orgs/{org_id}/roles/{role_id}."""

import uuid

import pytest

from tests.e2e.conftest import API, auth_headers, create_org_with_owner


@pytest.mark.e2e
class TestGetRole:
    """Получение роли по ID."""

    async def test_get_role_success(self, client) -> None:
        """200 — данные системной роли."""
        owner = await create_org_with_owner(client)
        roles_resp = await client.get(
            f"{API}/orgs/{owner['org_id']}/roles",
            headers=auth_headers(owner["access_token"]),
        )
        roles = roles_resp.json()["data"]
        if not roles:
            pytest.skip("Нет ролей")

        role_id = roles[0]["id"]
        resp = await client.get(
            f"{API}/orgs/{owner['org_id']}/roles/{role_id}",
            headers=auth_headers(owner["access_token"]),
        )

        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["id"] == role_id

    async def test_get_role_not_found(self, client) -> None:
        """404 — роль не найдена."""
        owner = await create_org_with_owner(client)
        resp = await client.get(
            f"{API}/orgs/{owner['org_id']}/roles/{uuid.uuid4()}",
            headers=auth_headers(owner["access_token"]),
        )
        assert resp.status_code == 404

    async def test_get_role_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.get(f"{API}/orgs/{uuid.uuid4()}/roles/{uuid.uuid4()}")
        assert resp.status_code == 401

"""E2E-тесты: GET /account/roles/{role_id}."""

import uuid

import pytest

from tests.e2e.conftest import API


@pytest.mark.e2e
class TestGetRole:
    """Получение роли по ID."""

    async def test_get_role_success(self, auth_client) -> None:
        """200 — роль найдена (используем первую из списка)."""
        roles_resp = await auth_client.get(f"{API}/account/roles")
        assert roles_resp.status_code == 200
        roles = roles_resp.json()["data"]

        if not roles:
            pytest.skip("Нет ролей в системе")

        role_id = roles[0]["id"]
        resp = await auth_client.get(f"{API}/account/roles/{role_id}")
        assert resp.status_code == 200
        assert resp.json()["data"]["id"] == role_id

    async def test_get_role_not_found(self, auth_client) -> None:
        """404 — роль не найдена."""
        fake_id = str(uuid.uuid4())
        resp = await auth_client.get(f"{API}/account/roles/{fake_id}")
        assert resp.status_code == 404

    async def test_get_role_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        fake_id = str(uuid.uuid4())
        resp = await client.get(f"{API}/account/roles/{fake_id}")
        assert resp.status_code == 401

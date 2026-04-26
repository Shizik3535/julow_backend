"""E2E-тесты: GET /account/me."""

import pytest

from tests.e2e.conftest import API


@pytest.mark.e2e
class TestGetMe:
    """Получение текущего пользователя."""

    async def test_get_me_success(self, auth_client, registered_user) -> None:
        """200 — возвращает данные текущего пользователя."""
        resp = await auth_client.get(f"{API}/account/me")

        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["email"] == registered_user["email"]
        assert data["id"] == registered_user["user_id"]

    async def test_get_me_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.get(f"{API}/account/me")
        assert resp.status_code == 401

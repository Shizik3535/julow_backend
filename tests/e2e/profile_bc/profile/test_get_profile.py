"""E2E-тесты: GET /profile/me."""

import pytest

from tests.e2e.conftest import API


@pytest.mark.e2e
class TestGetProfile:
    """Получение профиля текущего пользователя."""

    async def test_get_profile_success(self, auth_client) -> None:
        """200 — возвращает данные профиля."""
        resp = await auth_client.get(f"{API}/profile/me")

        assert resp.status_code == 200
        data = resp.json()["data"]
        assert "user_id" in data or "id" in data

    async def test_get_profile_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.get(f"{API}/profile/me")
        assert resp.status_code == 401

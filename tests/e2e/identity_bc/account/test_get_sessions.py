"""E2E-тесты: GET /account/sessions."""

import pytest

from tests.e2e.conftest import API


@pytest.mark.e2e
class TestGetSessions:
    """Получение активных сессий."""

    async def test_get_sessions_success(self, auth_client) -> None:
        """200 — список сессий (минимум 1 — текущая)."""
        resp = await auth_client.get(f"{API}/account/sessions")

        assert resp.status_code == 200
        data = resp.json()["data"]
        assert isinstance(data, list)
        assert len(data) >= 1

    async def test_get_sessions_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.get(f"{API}/account/sessions")
        assert resp.status_code == 401

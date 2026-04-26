"""E2E-тесты: GET /account/security/status."""

import pytest

from tests.e2e.conftest import API


@pytest.mark.e2e
class TestGetAuthStatus:
    """Обзор безопасности аккаунта."""

    async def test_get_auth_status_success(self, auth_client) -> None:
        """200 — возвращает статус безопасности."""
        resp = await auth_client.get(f"{API}/account/security/status")

        assert resp.status_code == 200
        data = resp.json()["data"]
        assert "has_password" in data

    async def test_get_auth_status_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.get(f"{API}/account/security/status")
        assert resp.status_code == 401

"""E2E-тесты: GET /account/security/oauth."""

import pytest

from tests.e2e.conftest import API


@pytest.mark.e2e
class TestGetOAuthLinks:
    """Список привязанных OAuth-провайдеров."""

    async def test_get_oauth_links_success(self, auth_client) -> None:
        """200 — возвращает список (может быть пустым)."""
        resp = await auth_client.get(f"{API}/account/security/oauth")

        assert resp.status_code == 200
        data = resp.json()["data"]
        assert isinstance(data, list)

    async def test_get_oauth_links_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.get(f"{API}/account/security/oauth")
        assert resp.status_code == 401

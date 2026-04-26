"""E2E-тесты: POST /account/me/disable."""

import pytest

from tests.e2e.conftest import API


@pytest.mark.e2e
class TestDisableAccount:
    """Деактивация аккаунта."""

    async def test_disable_account_success(self, auth_client) -> None:
        """200 — аккаунт деактивирован."""
        resp = await auth_client.post(f"{API}/account/me/disable")
        assert resp.status_code == 200

    async def test_disable_account_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.post(f"{API}/account/me/disable")
        assert resp.status_code == 401

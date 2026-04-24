"""E2E-тесты: POST /account/security/2fa/disable."""

import pytest

from tests.e2e.conftest import API, auth_headers, register_and_login


@pytest.mark.e2e
class TestDisableAuthFactor:
    """Отключение фактора 2FA."""

    async def test_disable_auth_factor_success(self, client) -> None:
        """200 — фактор отключён (после включения)."""
        user = await register_and_login(client)
        headers = auth_headers(user["access_token"])

        # Включаем TOTP
        enable_resp = await client.post(
            f"{API}/account/security/2fa/enable",
            json={"method": "totp", "is_primary": True},
            headers=headers,
        )
        assert enable_resp.status_code == 200

        # Отключаем
        resp = await client.post(
            f"{API}/account/security/2fa/disable",
            json={"method": "totp"},
            headers=headers,
        )
        assert resp.status_code == 200

    async def test_disable_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.post(
            f"{API}/account/security/2fa/disable",
            json={"method": "totp"},
        )
        assert resp.status_code == 401

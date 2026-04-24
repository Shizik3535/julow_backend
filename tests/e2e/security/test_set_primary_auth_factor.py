"""E2E-тесты: POST /account/security/2fa/set-primary."""

import pytest

from tests.e2e.conftest import API, auth_headers, register_and_login


@pytest.mark.e2e
class TestSetPrimaryAuthFactor:
    """Установка основного фактора 2FA."""

    async def test_set_primary_success(self, client) -> None:
        """200 — основной фактор установлен."""
        user = await register_and_login(client)
        headers = auth_headers(user["access_token"])

        # Включаем TOTP
        await client.post(
            f"{API}/account/security/2fa/enable",
            json={"method": "totp", "is_primary": False},
            headers=headers,
        )

        resp = await client.post(
            f"{API}/account/security/2fa/set-primary",
            json={"method": "totp"},
            headers=headers,
        )
        assert resp.status_code == 200

    async def test_set_primary_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.post(
            f"{API}/account/security/2fa/set-primary",
            json={"method": "totp"},
        )
        assert resp.status_code == 401

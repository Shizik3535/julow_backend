"""E2E-тесты: POST /account/security/2fa/verify."""

import pytest

from tests.e2e.conftest import API, auth_headers, register_and_login


@pytest.mark.e2e
class TestVerifyAuthFactor:
    """Проверка кода 2FA."""

    async def test_verify_invalid_code(self, client) -> None:
        """400 — неверный код 2FA."""
        user = await register_and_login(client)
        headers = auth_headers(user["access_token"])

        # Включаем TOTP
        await client.post(
            f"{API}/account/security/2fa/enable",
            json={"method": "totp", "is_primary": True},
            headers=headers
        )

        resp = await client.post(
            f"{API}/account/security/2fa/verify",
            json={"method": "totp", "code": "000000"},
            headers=headers
        )
        assert resp.status_code == 400

    async def test_verify_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.post(
            f"{API}/account/security/2fa/verify",
            json={"method": "totp", "code": "123456"}
        )
        assert resp.status_code == 401

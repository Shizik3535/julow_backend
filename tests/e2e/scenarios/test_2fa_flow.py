"""E2E-сценарий: enable 2FA → set-primary → disable."""

import pytest

from tests.e2e.conftest import API, auth_headers, register_and_login


@pytest.mark.e2e
class Test2FAFlow:
    """Полный цикл 2FA: включение, настройка, отключение."""

    async def test_enable_set_primary_disable(self, client) -> None:
        """enable TOTP → set-primary → disable TOTP."""
        user = await register_and_login(client)
        headers = auth_headers(user["access_token"])

        # 1. Включаем TOTP
        enable_resp = await client.post(
            f"{API}/account/security/2fa/enable",
            json={"method": "totp", "is_primary": False},
            headers=headers
        )
        assert enable_resp.status_code == 200

        # 2. Устанавливаем основным
        primary_resp = await client.post(
            f"{API}/account/security/2fa/set-primary",
            json={"method": "totp"},
            headers=headers
        )
        assert primary_resp.status_code == 200

        # 3. Отключаем
        disable_resp = await client.post(
            f"{API}/account/security/2fa/disable",
            json={"method": "totp"},
            headers=headers
        )
        assert disable_resp.status_code == 200

    async def test_verify_invalid_code_after_enable(self, client) -> None:
        """enable TOTP → verify с неверным кодом → 400."""
        user = await register_and_login(client)
        headers = auth_headers(user["access_token"])

        # Включаем TOTP
        await client.post(
            f"{API}/account/security/2fa/enable",
            json={"method": "totp", "is_primary": True},
            headers=headers
        )

        # Проверяем неверный код
        verify_resp = await client.post(
            f"{API}/account/security/2fa/verify",
            json={"method": "totp", "code": "000000"},
            headers=headers
        )
        assert verify_resp.status_code == 400

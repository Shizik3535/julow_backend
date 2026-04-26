"""E2E-тесты: POST /account/security/2fa/enable."""

import pytest

from tests.e2e.conftest import API


@pytest.mark.e2e
class TestEnableAuthFactor:
    """Включение фактора 2FA."""

    async def test_enable_totp_success(self, auth_client) -> None:
        """200 — TOTP-фактор включён, возвращает provisioning URI."""
        resp = await auth_client.post(
            f"{API}/account/security/2fa/enable",
            json={"method": "totp", "is_primary": True}
        )

        assert resp.status_code == 200
        data = resp.json()["data"]
        assert "provisioning_uri" in data or "method" in data

    async def test_enable_email_code(self, auth_client) -> None:
        """200 — email_code-фактор включён."""
        resp = await auth_client.post(
            f"{API}/account/security/2fa/enable",
            json={"method": "email_code", "is_primary": False}
        )
        assert resp.status_code == 200

    async def test_enable_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.post(
            f"{API}/account/security/2fa/enable",
            json={"method": "totp", "is_primary": True}
        )
        assert resp.status_code == 401

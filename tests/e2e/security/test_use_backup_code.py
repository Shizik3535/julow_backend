"""E2E-тесты: POST /account/security/2fa/use-backup-code."""

import pytest

from tests.e2e.conftest import API, auth_headers, register_and_login


@pytest.mark.e2e
class TestUseBackupCode:
    """Использование резервного кода 2FA."""

    async def test_use_backup_code_success(self, client) -> None:
        """200 — резервный код использован."""
        user = await register_and_login(client)
        headers = auth_headers(user["access_token"])

        # Включаем 2FA (TOTP)
        enable_resp = await client.post(
            f"{API}/account/security/2fa/enable",
            json={"method": "totp", "is_primary": True},
            headers=headers,
        )
        assert enable_resp.status_code == 200

        # Генерируем коды
        gen_resp = await client.post(
            f"{API}/account/security/2fa/backup-codes",
            json={"count": 5},
            headers=headers,
        )
        assert gen_resp.status_code == 200
        codes = gen_resp.json()["data"]["codes"]

        # Используем первый код
        resp = await client.post(
            f"{API}/account/security/2fa/use-backup-code",
            json={"code": codes[0]},
            headers=headers,
        )
        assert resp.status_code == 200

    async def test_use_invalid_code(self, client) -> None:
        """400 — неверный резервный код."""
        user = await register_and_login(client)
        resp = await client.post(
            f"{API}/account/security/2fa/use-backup-code",
            json={"code": "INVALIDCODE"},
            headers=auth_headers(user["access_token"]),
        )
        assert resp.status_code == 400

    async def test_use_backup_code_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.post(
            f"{API}/account/security/2fa/use-backup-code",
            json={"code": "TESTCODE"},
        )
        assert resp.status_code == 401

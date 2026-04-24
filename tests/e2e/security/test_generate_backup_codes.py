"""E2E-тесты: POST /account/security/2fa/backup-codes."""

import pytest

from tests.e2e.conftest import API


@pytest.mark.e2e
class TestGenerateBackupCodes:
    """Генерация резервных кодов 2FA."""

    async def test_generate_backup_codes_success(self, auth_client) -> None:
        """200 — резервные коды сгенерированы."""
        resp = await auth_client.post(
            f"{API}/account/security/2fa/backup-codes",
            json={"count": 10},
        )

        assert resp.status_code == 200
        data = resp.json()["data"]
        assert "codes" in data
        assert len(data["codes"]) == 10

    async def test_generate_custom_count(self, auth_client) -> None:
        """200 — кастомное количество кодов."""
        resp = await auth_client.post(
            f"{API}/account/security/2fa/backup-codes",
            json={"count": 5},
        )

        assert resp.status_code == 200
        data = resp.json()["data"]
        assert len(data["codes"]) == 5

    async def test_generate_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.post(
            f"{API}/account/security/2fa/backup-codes",
            json={"count": 10},
        )
        assert resp.status_code == 401

"""E2E-сценарий: generate backup codes → use one code."""

import pytest

from tests.e2e.conftest import API, auth_headers, register_and_login


@pytest.mark.e2e
class TestBackupCodesFlow:
    """Полный цикл резервных кодов: генерация → использование."""

    async def test_generate_then_use_code(self, client) -> None:
        """generate → use first code → успех."""
        user = await register_and_login(client)
        headers = auth_headers(user["access_token"])

        # 0. Включаем 2FA (TOTP)
        enable_resp = await client.post(
            f"{API}/account/security/2fa/enable",
            json={"method": "totp", "is_primary": True},
            headers=headers
        )
        assert enable_resp.status_code == 200

        # 1. Генерируем коды
        gen_resp = await client.post(
            f"{API}/account/security/2fa/backup-codes",
            json={"count": 5},
            headers=headers
        )
        assert gen_resp.status_code == 200
        codes = gen_resp.json()["data"]["codes"]
        assert len(codes) == 5

        # 2. Используем первый код
        use_resp = await client.post(
            f"{API}/account/security/2fa/use-backup-code",
            json={"code": codes[0]},
            headers=headers
        )
        assert use_resp.status_code == 200

    async def test_reuse_code_fails(self, client) -> None:
        """Повторное использование одного кода — 400."""
        user = await register_and_login(client)
        headers = auth_headers(user["access_token"])

        # Включаем 2FA (TOTP)
        enable_resp = await client.post(
            f"{API}/account/security/2fa/enable",
            json={"method": "totp", "is_primary": True},
            headers=headers
        )
        assert enable_resp.status_code == 200

        # Генерируем
        gen_resp = await client.post(
            f"{API}/account/security/2fa/backup-codes",
            json={"count": 3},
            headers=headers
        )
        codes = gen_resp.json()["data"]["codes"]

        # Первое использование — успех
        use1 = await client.post(
            f"{API}/account/security/2fa/use-backup-code",
            json={"code": codes[0]},
            headers=headers
        )
        assert use1.status_code == 200

        # Повторное — ошибка
        use2 = await client.post(
            f"{API}/account/security/2fa/use-backup-code",
            json={"code": codes[0]},
            headers=headers
        )
        assert use2.status_code == 400

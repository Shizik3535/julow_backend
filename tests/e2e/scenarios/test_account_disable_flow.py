"""E2E-сценарий: disable → reactivate → проверка статуса."""

import pytest

from tests.e2e.conftest import API, auth_headers, register_and_login


@pytest.mark.e2e
class TestAccountDisableFlow:
    """Цикл деактивации и реактивации аккаунта."""

    async def test_disable_then_reactivate(self, client) -> None:
        """disable → reactivate → get_me (аккаунт активен)."""
        user = await register_and_login(client)
        headers = auth_headers(user["access_token"])

        # 1. Деактивация
        disable_resp = await client.post(
            f"{API}/account/me/disable", headers=headers
        )
        assert disable_resp.status_code == 200

        # 2. Реактивация
        react_resp = await client.post(
            f"{API}/account/me/reactivate", headers=headers
        )
        assert react_resp.status_code == 200

        # 3. Проверяем, что аккаунт доступен
        me_resp = await client.get(f"{API}/account/me", headers=headers)
        assert me_resp.status_code == 200

    async def test_reactivate_without_disable_fails(self, client) -> None:
        """409 — реактивация без предварительной деактивации."""
        user = await register_and_login(client)
        resp = await client.post(
            f"{API}/account/me/reactivate",
            headers=auth_headers(user["access_token"])
        )
        assert resp.status_code == 409

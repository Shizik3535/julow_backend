"""E2E-тесты: POST /account/me/reactivate."""

import pytest

from tests.e2e.conftest import API, auth_headers, register_and_login


@pytest.mark.e2e
class TestReactivateAccount:
    """Реактивация аккаунта."""

    async def test_reactivate_success(self, client) -> None:
        """200 — реактивация после disable."""
        user = await register_and_login(client)
        headers = auth_headers(user["access_token"])

        # Сначала деактивируем
        resp = await client.post(f"{API}/account/me/disable", headers=headers)
        assert resp.status_code == 200

        # Затем реактивируем
        resp = await client.post(f"{API}/account/me/reactivate", headers=headers)
        assert resp.status_code == 200

    async def test_reactivate_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.post(f"{API}/account/me/reactivate")
        assert resp.status_code == 401

    async def test_reactivate_without_disable(self, client) -> None:
        """409 — реактивация без предварительной деактивации."""
        user = await register_and_login(client)
        resp = await client.post(
            f"{API}/account/me/reactivate",
            headers=auth_headers(user["access_token"]),
        )
        assert resp.status_code == 409

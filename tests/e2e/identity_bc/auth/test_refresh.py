"""E2E-тесты: POST /auth/refresh."""

import pytest

from tests.e2e.conftest import API, register_and_login


@pytest.mark.e2e
class TestRefresh:
    """Обновление пары токенов."""

    async def test_refresh_success(self, client) -> None:
        """200 — успешное обновление токенов."""
        user = await register_and_login(client)
        resp = await client.post(
            f"{API}/auth/refresh",
            json={"refresh_token": user["refresh_token"]}
        )

        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["access_token"]
        assert data["refresh_token"]

    async def test_refresh_invalid_token(self, client) -> None:
        """401 — невалидный refresh-токен."""
        resp = await client.post(
            f"{API}/auth/refresh",
            json={"refresh_token": "invalid-token-value"}
        )
        assert resp.status_code == 401

    async def test_refresh_empty_token(self, client) -> None:
        """422 — пустой refresh-токен."""
        resp = await client.post(
            f"{API}/auth/refresh",
            json={"refresh_token": ""}
        )
        assert resp.status_code == 422

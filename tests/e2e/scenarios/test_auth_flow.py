"""E2E-сценарий: register → login → refresh → повторный access."""

import pytest

from tests.e2e.conftest import API, DEFAULT_PASSWORD, auth_headers, register_user


@pytest.mark.e2e
class TestAuthFlow:
    """Полный цикл аутентификации."""

    async def test_register_login_refresh_flow(self, client) -> None:
        """Регистрация → логин → refresh → использование нового access-токена."""
        # 1. Регистрация
        reg = await register_user(client)
        assert reg["response"].status_code == 201
        email = reg["email"]

        # 2. Логин
        login_resp = await client.post(
            f"{API}/auth/login",
            json={"email": email, "password": DEFAULT_PASSWORD},
        )
        assert login_resp.status_code == 200
        login_data = login_resp.json()["data"]
        access_token = login_data["access_token"]
        refresh_token = login_data["refresh_token"]

        # 3. Проверяем access-токен через /account/me
        me_resp = await client.get(
            f"{API}/account/me", headers=auth_headers(access_token)
        )
        assert me_resp.status_code == 200
        assert me_resp.json()["data"]["email"] == email

        # 4. Refresh
        refresh_resp = await client.post(
            f"{API}/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert refresh_resp.status_code == 200
        new_access = refresh_resp.json()["data"]["access_token"]
        assert new_access != access_token

        # 5. Проверяем новый access-токен
        me_resp2 = await client.get(
            f"{API}/account/me", headers=auth_headers(new_access)
        )
        assert me_resp2.status_code == 200
        assert me_resp2.json()["data"]["email"] == email

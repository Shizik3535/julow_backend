"""E2E-тесты: POST /auth/login."""

import pytest

from tests.e2e.conftest import API, DEFAULT_PASSWORD, register_user


@pytest.mark.e2e
class TestLogin:
    """Вход в систему."""

    async def test_login_success(self, client) -> None:
        """200 — успешный логин, возвращает токены и пользователя."""
        reg = await register_user(client)
        resp = await client.post(
            f"{API}/auth/login",
            json={"email": reg["email"], "password": DEFAULT_PASSWORD}
        )

        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["access_token"]
        assert data["refresh_token"]
        assert data["user"]["email"] == reg["email"]

    async def test_login_wrong_password(self, client) -> None:
        """401 — неверный пароль."""
        reg = await register_user(client)
        resp = await client.post(
            f"{API}/auth/login",
            json={"email": reg["email"], "password": "WrongP@ssword1"}
        )
        assert resp.status_code == 401

    async def test_login_nonexistent_user(self, client) -> None:
        """401 — несуществующий пользователь."""
        resp = await client.post(
            f"{API}/auth/login",
            json={"email": "ghost@example.com", "password": "StrongP@ss1"}
        )
        assert resp.status_code == 401

    async def test_login_remember_me(self, client) -> None:
        """200 — логин с is_remember_me=True."""
        reg = await register_user(client)
        resp = await client.post(
            f"{API}/auth/login",
            json={
                "email": reg["email"],
                "password": DEFAULT_PASSWORD,
                "is_remember_me": True,
            }
        )

        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["access_token"]
        assert data["refresh_token"]

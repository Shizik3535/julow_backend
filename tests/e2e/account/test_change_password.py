"""E2E-тесты: POST /account/me/change-password."""

import pytest

from tests.e2e.conftest import API, DEFAULT_PASSWORD, auth_headers, register_and_login


@pytest.mark.e2e
class TestChangePassword:
    """Смена пароля."""

    async def test_change_password_success(self, client) -> None:
        """200 — успешная смена пароля."""
        user = await register_and_login(client)
        resp = await client.post(
            f"{API}/account/me/change-password",
            json={
                "current_password": DEFAULT_PASSWORD,
                "new_password": "NewStr0ngP@ss!",
            },
            headers=auth_headers(user["access_token"]),
        )
        assert resp.status_code == 200

    async def test_change_password_wrong_current(self, client) -> None:
        """401 — неверный текущий пароль."""
        user = await register_and_login(client)
        resp = await client.post(
            f"{API}/account/me/change-password",
            json={
                "current_password": "WrongP@ssword1",
                "new_password": "NewStr0ngP@ss!",
            },
            headers=auth_headers(user["access_token"]),
        )
        assert resp.status_code == 401

    async def test_change_password_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.post(
            f"{API}/account/me/change-password",
            json={
                "current_password": DEFAULT_PASSWORD,
                "new_password": "NewStr0ngP@ss!",
            },
        )
        assert resp.status_code == 401

    async def test_change_password_short_new(self, client) -> None:
        """422 — новый пароль слишком короткий."""
        user = await register_and_login(client)
        resp = await client.post(
            f"{API}/account/me/change-password",
            json={
                "current_password": DEFAULT_PASSWORD,
                "new_password": "123",
            },
            headers=auth_headers(user["access_token"]),
        )
        assert resp.status_code == 422

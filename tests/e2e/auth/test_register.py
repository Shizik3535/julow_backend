"""E2E-тесты: POST /auth/register."""

import pytest

from tests.e2e.conftest import API, register_user


@pytest.mark.e2e
class TestRegister:
    """Регистрация нового пользователя."""

    async def test_register_success(self, client) -> None:
        """201 — успешная регистрация."""
        result = await register_user(client)
        resp = result["response"]

        assert resp.status_code == 201
        body = resp.json()
        assert body["data"]["id"]
        assert body["data"]["email"] == result["email"]

    async def test_register_duplicate_email(self, client) -> None:
        """409 — повторная регистрация с тем же email."""
        result = await register_user(client)
        assert result["response"].status_code == 201

        duplicate = await register_user(client, email=result["email"])
        assert duplicate["response"].status_code == 409

    async def test_register_invalid_email(self, client) -> None:
        """422 — невалидный email."""
        resp = await client.post(
            f"{API}/auth/register",
            json={"email": "not-an-email", "password": "StrongP@ss1"},
        )
        assert resp.status_code == 422

    async def test_register_short_password(self, client) -> None:
        """422 — пароль менее 8 символов."""
        resp = await client.post(
            f"{API}/auth/register",
            json={"email": "short@example.com", "password": "123"},
        )
        assert resp.status_code == 422

    async def test_register_missing_fields(self, client) -> None:
        """422 — отсутствуют обязательные поля."""
        resp = await client.post(f"{API}/auth/register", json={})
        assert resp.status_code == 422

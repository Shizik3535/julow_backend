"""E2E-тесты: POST /auth/password-reset/confirm."""

import pytest

from tests.e2e.conftest import API


@pytest.mark.e2e
class TestPasswordResetConfirm:
    """Подтверждение сброса пароля."""

    async def test_confirm_invalid_token(self, client) -> None:
        """400 — невалидный токен сброса."""
        resp = await client.post(
            f"{API}/auth/password-reset/confirm",
            json={
                "email": "user@example.com",
                "token": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
                "new_password": "NewStr0ngP@ss!",
            },
        )
        assert resp.status_code in (400, 404)

    async def test_confirm_short_token(self, client) -> None:
        """422 — токен слишком короткий."""
        resp = await client.post(
            f"{API}/auth/password-reset/confirm",
            json={
                "email": "user@example.com",
                "token": "short",
                "new_password": "NewStr0ngP@ss!",
            },
        )
        assert resp.status_code == 422

    async def test_confirm_short_password(self, client) -> None:
        """422 — новый пароль слишком короткий."""
        resp = await client.post(
            f"{API}/auth/password-reset/confirm",
            json={
                "email": "user@example.com",
                "token": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
                "new_password": "123",
            },
        )
        assert resp.status_code == 422

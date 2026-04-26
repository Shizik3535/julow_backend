"""E2E-тесты: POST /auth/confirm-email."""

import pytest

from tests.e2e.conftest import API, auth_headers, register_and_login


@pytest.mark.e2e
class TestConfirmEmail:
    """Подтверждение email-адреса."""

    async def test_confirm_email_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.post(
            f"{API}/auth/confirm-email",
            json={"token": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"}
        )
        assert resp.status_code == 401

    async def test_confirm_email_invalid_token(self, client) -> None:
        """400 — невалидный токен подтверждения."""
        user = await register_and_login(client)
        resp = await client.post(
            f"{API}/auth/confirm-email",
            json={"token": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"},
            headers=auth_headers(user["access_token"])
        )
        assert resp.status_code in (400, 404, 409)

    async def test_confirm_email_short_token(self, client) -> None:
        """422 — токен слишком короткий (< 16 символов)."""
        user = await register_and_login(client)
        resp = await client.post(
            f"{API}/auth/confirm-email",
            json={"token": "short"},
            headers=auth_headers(user["access_token"])
        )
        assert resp.status_code == 422

"""E2E-тесты: POST /auth/password-reset/request."""

import pytest

from tests.e2e.conftest import API, register_user


@pytest.mark.e2e
class TestPasswordResetRequest:
    """Запрос сброса пароля."""

    async def test_request_existing_email(self, client) -> None:
        """200 — запрос для существующего email."""
        reg = await register_user(client)
        resp = await client.post(
            f"{API}/auth/password-reset/request",
            json={"email": reg["email"]}
        )
        assert resp.status_code == 200

    async def test_request_nonexistent_email(self, client) -> None:
        """200 — запрос для несуществующего email (не раскрывает факт отсутствия)."""
        resp = await client.post(
            f"{API}/auth/password-reset/request",
            json={"email": "nobody@example.com"}
        )
        assert resp.status_code == 200

    async def test_request_invalid_email(self, client) -> None:
        """422 — невалидный формат email."""
        resp = await client.post(
            f"{API}/auth/password-reset/request",
            json={"email": "not-an-email"}
        )
        assert resp.status_code == 422

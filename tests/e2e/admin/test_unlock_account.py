"""E2E-тесты: POST /admin/users/{user_id}/unlock."""

import uuid

import pytest

from tests.e2e.conftest import API, auth_headers, register_and_login, register_admin_and_login


@pytest.mark.e2e
class TestUnlockAccount:
    """Разблокировка аккаунта пользователя."""

    async def test_unlock_account_success(self, client) -> None:
        """200 — аккаунт разблокирован (admin-пользователь)."""
        admin = await register_admin_and_login(client)
        target = await register_and_login(client)
        resp = await client.post(
            f"{API}/admin/users/{target['user_id']}/unlock",
            headers=auth_headers(admin["access_token"]),
        )
        assert resp.status_code == 200

    async def test_unlock_account_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        fake_uid = str(uuid.uuid4())
        resp = await client.post(f"{API}/admin/users/{fake_uid}/unlock")
        assert resp.status_code == 401

    async def test_unlock_account_not_found(self, client) -> None:
        """404 — пользователь не найден."""
        admin = await register_admin_and_login(client)
        fake_uid = str(uuid.uuid4())
        resp = await client.post(
            f"{API}/admin/users/{fake_uid}/unlock",
            headers=auth_headers(admin["access_token"]),
        )
        assert resp.status_code == 404

    async def test_unlock_account_forbidden(self, client) -> None:
        """403 — обычный пользователь не может разблокировать аккаунты."""
        user = await register_and_login(client)
        fake_uid = str(uuid.uuid4())
        resp = await client.post(
            f"{API}/admin/users/{fake_uid}/unlock",
            headers=auth_headers(user["access_token"]),
        )
        assert resp.status_code == 403

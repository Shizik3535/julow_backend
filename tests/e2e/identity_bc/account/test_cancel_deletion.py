"""E2E-тесты: POST /account/me/cancel-deletion."""

import pytest

from tests.e2e.conftest import API, auth_headers, register_and_login


@pytest.mark.e2e
class TestCancelDeletion:
    """Отмена удаления аккаунта."""

    async def test_cancel_deletion_success(self, client) -> None:
        """200 — отмена удаления после request-deletion."""
        user = await register_and_login(client)
        headers = auth_headers(user["access_token"])

        # Сначала запрашиваем удаление
        resp = await client.post(
            f"{API}/account/me/request-deletion", headers=headers
        )
        assert resp.status_code == 200

        # Затем отменяем
        resp = await client.post(
            f"{API}/account/me/cancel-deletion", headers=headers
        )
        assert resp.status_code == 200

    async def test_cancel_deletion_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.post(f"{API}/account/me/cancel-deletion")
        assert resp.status_code == 401

    async def test_cancel_deletion_without_request(self, client) -> None:
        """409 — отмена без предварительного запроса удаления."""
        user = await register_and_login(client)
        resp = await client.post(
            f"{API}/account/me/cancel-deletion",
            headers=auth_headers(user["access_token"])
        )
        assert resp.status_code == 409

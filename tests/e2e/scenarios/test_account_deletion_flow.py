"""E2E-сценарий: request-deletion → cancel-deletion → проверка статуса."""

import pytest

from tests.e2e.conftest import API, auth_headers, register_and_login


@pytest.mark.e2e
class TestAccountDeletionFlow:
    """Цикл запроса и отмены удаления аккаунта."""

    async def test_request_then_cancel_deletion(self, client) -> None:
        """request-deletion → cancel-deletion → get_me (аккаунт активен)."""
        user = await register_and_login(client)
        headers = auth_headers(user["access_token"])

        # 1. Запрос удаления
        req_resp = await client.post(
            f"{API}/account/me/request-deletion", headers=headers
        )
        assert req_resp.status_code == 200

        # 2. Отмена удаления
        cancel_resp = await client.post(
            f"{API}/account/me/cancel-deletion", headers=headers
        )
        assert cancel_resp.status_code == 200

        # 3. Проверяем, что аккаунт доступен
        me_resp = await client.get(f"{API}/account/me", headers=headers)
        assert me_resp.status_code == 200
        assert me_resp.json()["data"]["email"] == user["email"]

    async def test_cancel_without_request_fails(self, client) -> None:
        """409 — отмена без предварительного запроса."""
        user = await register_and_login(client)
        resp = await client.post(
            f"{API}/account/me/cancel-deletion",
            headers=auth_headers(user["access_token"])
        )
        assert resp.status_code == 409

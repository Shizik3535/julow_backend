"""E2E-тесты: POST /account/me/request-deletion."""

import pytest

from tests.e2e.conftest import API


@pytest.mark.e2e
class TestRequestDeletion:
    """Запрос удаления аккаунта."""

    async def test_request_deletion_success(self, auth_client) -> None:
        """200 — запрос удаления принят."""
        resp = await auth_client.post(f"{API}/account/me/request-deletion")
        assert resp.status_code == 200

    async def test_request_deletion_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.post(f"{API}/account/me/request-deletion")
        assert resp.status_code == 401

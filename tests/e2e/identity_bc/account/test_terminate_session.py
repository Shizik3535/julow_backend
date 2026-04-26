"""E2E-тесты: DELETE /account/sessions/{session_id}."""

import uuid

import pytest

from tests.e2e.conftest import API, auth_headers, register_and_login


@pytest.mark.e2e
class TestTerminateSession:
    """Завершение одной сессии."""

    async def test_terminate_session_success(self, client) -> None:
        """200 — сессия завершена."""
        user = await register_and_login(client)
        headers = auth_headers(user["access_token"])

        # Получаем список сессий
        sessions_resp = await client.get(f"{API}/account/sessions", headers=headers)
        assert sessions_resp.status_code == 200
        sessions = sessions_resp.json()["data"]
        assert len(sessions) >= 1

        session_id = sessions[0]["id"]
        resp = await client.delete(
            f"{API}/account/sessions/{session_id}", headers=headers
        )
        assert resp.status_code == 200

    async def test_terminate_session_not_found(self, client) -> None:
        """404 — сессия не найдена."""
        user = await register_and_login(client)
        fake_id = str(uuid.uuid4())
        resp = await client.delete(
            f"{API}/account/sessions/{fake_id}",
            headers=auth_headers(user["access_token"])
        )
        assert resp.status_code == 404

    async def test_terminate_session_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        fake_id = str(uuid.uuid4())
        resp = await client.delete(f"{API}/account/sessions/{fake_id}")
        assert resp.status_code == 401

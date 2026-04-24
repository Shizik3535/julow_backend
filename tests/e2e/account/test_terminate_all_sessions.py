"""E2E-тесты: DELETE /account/sessions (все кроме текущей)."""

import uuid

import pytest

from tests.e2e.conftest import API, auth_headers, register_and_login


@pytest.mark.e2e
class TestTerminateAllSessions:
    """Завершение всех сессий кроме текущей."""

    async def test_terminate_all_sessions_success(self, client) -> None:
        """200 — все сессии завершены (кроме текущей)."""
        user = await register_and_login(client)
        headers = auth_headers(user["access_token"])

        # Получаем текущую сессию
        sessions_resp = await client.get(f"{API}/account/sessions", headers=headers)
        assert sessions_resp.status_code == 200
        sessions = sessions_resp.json()["data"]
        current_session_id = sessions[0]["id"]

        resp = await client.request(
            "DELETE",
            f"{API}/account/sessions",
            headers=headers,
            json={"current_session_id": current_session_id},
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert "terminated_count" in data

    async def test_terminate_all_sessions_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.request(
            "DELETE",
            f"{API}/account/sessions",
            json={"current_session_id": str(uuid.uuid4())},
        )
        assert resp.status_code == 401

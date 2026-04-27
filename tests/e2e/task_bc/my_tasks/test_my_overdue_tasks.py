"""E2E-тесты: GET /tasks/mine/overdue — Мои просроченные задачи."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    register_and_login,
)


@pytest.mark.e2e
class TestMyOverdueTasks:
    """Мои просроченные задачи."""

    async def test_my_overdue_tasks_success(self, client: AsyncClient):
        """200 — список просроченных задач."""
        user = await register_and_login(client)
        resp = await client.get(
            f"{API}/tasks/mine/overdue",
            headers=auth_headers(user["access_token"])
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "total" in data

    async def test_my_overdue_tasks_empty(self, client: AsyncClient):
        """200 — пустой список просроченных задач."""
        user = await register_and_login(client)
        resp = await client.get(
            f"{API}/tasks/mine/overdue",
            headers=auth_headers(user["access_token"])
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0
        assert len(data["items"]) == 0

    async def test_my_overdue_tasks_no_auth(self, client: AsyncClient):
        """401 — без токена авторизации."""
        resp = await client.get(f"{API}/tasks/mine/overdue")
        assert resp.status_code == 401

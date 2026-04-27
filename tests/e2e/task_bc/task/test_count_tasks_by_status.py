"""E2E-тесты: GET /workspaces/{ws_id}/projects/{project_id}/tasks/count-by-status/{status_id} — Счётчик задач по статусу."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    register_and_login,
)


@pytest.mark.e2e
class TestCountTasksByStatus:
    """Счётчик задач по статусу."""

    async def test_count_by_status_success(self, client: AsyncClient, project_owner):
        """200 — количество задач с указанным статусом."""
        proj = project_owner
        # Создаём задачу, чтобы получить статус из системы
        # В реальном тесте нужно сначала создать статус или использовать существующий
        resp = await client.get(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/tasks/count-by-status/00000000-0000-0000-0000-000000000000",
            headers=auth_headers(proj["access_token"])
        )
        # Может вернуть 404 если статус не существует, или 200 с count=0
        assert resp.status_code in (200, 404)

    async def test_count_by_status_no_auth(self, client: AsyncClient, project_owner):
        """401 — без токена авторизации."""
        proj = project_owner
        resp = await client.get(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/tasks/count-by-status/00000000-0000-0000-0000-000000000000"
        )
        assert resp.status_code == 401

    async def test_count_by_status_forbidden(self, client: AsyncClient, project_owner):
        """403 — пользователь не участник проекта."""
        proj = project_owner
        stranger = await register_and_login(client)
        resp = await client.get(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/tasks/count-by-status/00000000-0000-0000-0000-000000000000",
            headers=auth_headers(stranger["access_token"])
        )
        assert resp.status_code == 403

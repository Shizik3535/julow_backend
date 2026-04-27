"""E2E-тесты: GET /workspaces/{ws_id}/projects/{project_id}/tasks/count — Счётчик задач."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    create_task,
    register_and_login,
)


@pytest.mark.e2e
class TestCountTasks:
    """Счётчик задач проекта."""

    async def test_count_success(self, client: AsyncClient, project_owner):
        """200 — количество задач в проекте."""
        proj = project_owner
        await create_task(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        await create_task(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        resp = await client.get(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/tasks/count",
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert "count" in data
        assert data["count"] >= 2

    async def test_count_empty(self, client: AsyncClient, project_owner):
        """200 — ноль задач в проекте."""
        proj = project_owner
        resp = await client.get(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/tasks/count",
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["count"] == 0

    async def test_count_no_auth(self, client: AsyncClient, project_owner):
        """401 — без токена авторизации."""
        proj = project_owner
        resp = await client.get(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/tasks/count"
        )
        assert resp.status_code == 401

    async def test_count_forbidden(self, client: AsyncClient, project_owner):
        """403 — пользователь не участник проекта."""
        proj = project_owner
        stranger = await register_and_login(client)
        resp = await client.get(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/tasks/count",
            headers=auth_headers(stranger["access_token"])
        )
        assert resp.status_code == 403

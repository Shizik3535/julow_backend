"""E2E-тесты: POST /tasks/{task_id}/archive — Архивирование задачи."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    create_task,
    register_and_login,
)


@pytest.mark.e2e
class TestArchiveTask:
    """Архивирование задачи."""

    async def test_archive_task_success(self, client: AsyncClient, project_owner):
        """200 — задача архивирована."""
        proj = project_owner
        task = await create_task(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        resp = await client.post(
            f"{API}/tasks/{task['task_id']}/archive",
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 200

    async def test_archive_task_no_auth(self, client: AsyncClient, project_owner):
        """401 — без токена авторизации."""
        proj = project_owner
        task = await create_task(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        resp = await client.post(f"{API}/tasks/{task['task_id']}/archive")
        assert resp.status_code == 401

    async def test_archive_task_forbidden(self, client: AsyncClient, project_owner):
        """403 — пользователь не участник проекта."""
        proj = project_owner
        task = await create_task(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        stranger = await register_and_login(client)
        resp = await client.post(
            f"{API}/tasks/{task['task_id']}/archive",
            headers=auth_headers(stranger["access_token"])
        )
        assert resp.status_code == 403

    async def test_archive_task_not_found(self, client: AsyncClient, project_owner):
        """404 — задача не найдена."""
        proj = project_owner
        resp = await client.post(
            f"{API}/tasks/00000000-0000-0000-0000-000000000000/archive",
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 404

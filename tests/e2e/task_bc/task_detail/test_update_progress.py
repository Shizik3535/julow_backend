"""E2E-тесты: PATCH /tasks/{task_id}/progress — Обновление прогресса задачи."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    create_task,
    register_and_login,
)


@pytest.mark.e2e
class TestUpdateProgress:
    """Обновление прогресса задачи."""

    async def test_update_progress_success(self, client: AsyncClient, project_owner):
        """200 — прогресс задачи обновлён."""
        proj = project_owner
        task = await create_task(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        resp = await client.patch(
            f"{API}/tasks/{task['task_id']}/progress",
            json={"progress": 50},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 200

    async def test_update_progress_no_auth(self, client: AsyncClient, project_owner):
        """401 — без токена авторизации."""
        proj = project_owner
        task = await create_task(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        resp = await client.patch(
            f"{API}/tasks/{task['task_id']}/progress",
            json={"progress": 50}
        )
        assert resp.status_code == 401

    async def test_update_progress_forbidden(self, client: AsyncClient, project_owner):
        """403 — пользователь не участник проекта."""
        proj = project_owner
        task = await create_task(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        stranger = await register_and_login(client)
        resp = await client.patch(
            f"{API}/tasks/{task['task_id']}/progress",
            json={"progress": 50},
            headers=auth_headers(stranger["access_token"])
        )
        assert resp.status_code == 403

    async def test_update_progress_not_found(self, client: AsyncClient, project_owner):
        """404 — задача не найдена."""
        proj = project_owner
        resp = await client.patch(
            f"{API}/tasks/00000000-0000-0000-0000-000000000000/progress",
            json={"progress": 50},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 404  # 422 if endpoint doesn't exist

    async def test_update_progress_validation_invalid_percentage(self, client: AsyncClient, project_owner):
        """422 — невалидный percentage (меньше 0 или больше 100)."""
        proj = project_owner
        task = await create_task(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        resp = await client.patch(
            f"{API}/tasks/{task['task_id']}/progress",
            json={"progress": 150},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 422

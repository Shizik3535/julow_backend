"""E2E-тесты: PATCH /tasks/{task_id} — Обновление информации задачи."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    create_task,
    register_and_login,
)


@pytest.mark.e2e
class TestUpdateTaskInfo:
    """Обновление информации задачи."""

    async def test_update_task_info_success(self, client: AsyncClient, project_owner):
        """200 — информация задачи обновлена."""
        proj = project_owner
        task = await create_task(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        resp = await client.patch(
            f"{API}/tasks/{task['task_id']}",
            json={"title": "Updated Title", "description_content": "New description"},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["message"]

    async def test_update_task_info_no_auth(self, client: AsyncClient, project_owner):
        """401 — без токена авторизации."""
        proj = project_owner
        task = await create_task(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        resp = await client.patch(
            f"{API}/tasks/{task['task_id']}",
            json={"title": "Updated Title"}
        )
        assert resp.status_code == 401

    async def test_update_task_info_forbidden(self, client: AsyncClient, project_owner):
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
            f"{API}/tasks/{task['task_id']}",
            json={"title": "Updated Title"},
            headers=auth_headers(stranger["access_token"])
        )
        assert resp.status_code == 403

    async def test_update_task_info_not_found(self, client: AsyncClient, project_owner):
        """404 — задача не найдена."""
        proj = project_owner
        resp = await client.patch(
            f"{API}/tasks/00000000-0000-0000-0000-000000000000",
            json={"title": "Updated Title"},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 404

    async def test_update_task_info_validation_empty_title(self, client: AsyncClient, project_owner):
        """422 — пустой title."""
        proj = project_owner
        task = await create_task(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        resp = await client.patch(
            f"{API}/tasks/{task['task_id']}",
            json={"title": ""},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 422

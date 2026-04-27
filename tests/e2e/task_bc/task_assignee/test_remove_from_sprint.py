"""E2E-тесты: DELETE /tasks/{task_id}/sprint — Удаление задачи из спринта."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    create_task,
    register_and_login,
)


@pytest.mark.e2e
class TestRemoveFromSprint:
    """Удаление задачи из спринта."""

    async def test_remove_from_sprint_success(self, client: AsyncClient, project_owner):
        """200 — задача удалена из спринта."""
        proj = project_owner
        task = await create_task(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        # Сначала привязываем к спринту
        await client.post(
            f"{API}/tasks/{task['task_id']}/sprint",
            json={"sprint_id": "00000000-0000-0000-0000-000000000001"},
            headers=auth_headers(proj["access_token"])
        )
        # Затем удаляем
        resp = await client.delete(
            f"{API}/tasks/{task['task_id']}/sprint",
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 200

    async def test_remove_from_sprint_no_auth(self, client: AsyncClient, project_owner):
        """401 — без токена авторизации."""
        proj = project_owner
        task = await create_task(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        resp = await client.delete(f"{API}/tasks/{task['task_id']}/sprint")
        assert resp.status_code == 401

    async def test_remove_from_sprint_forbidden(self, client: AsyncClient, project_owner):
        """403 — пользователь не участник проекта."""
        proj = project_owner
        task = await create_task(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        stranger = await register_and_login(client)
        resp = await client.delete(
            f"{API}/tasks/{task['task_id']}/sprint",
            headers=auth_headers(stranger["access_token"])
        )
        assert resp.status_code == 403

    async def test_remove_from_sprint_not_found(self, client: AsyncClient, project_owner):
        """404 — задача не найдена."""
        proj = project_owner
        resp = await client.delete(
            f"{API}/tasks/00000000-0000-0000-0000-000000000000/sprint",
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 404

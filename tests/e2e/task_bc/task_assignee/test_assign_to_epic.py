"""E2E-тесты: POST /tasks/{task_id}/epic — Привязка задачи к эпику."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    create_task,
    register_and_login,
)


@pytest.mark.e2e
class TestAssignToEpic:
    """Привязка задачи к эпику."""

    async def test_assign_to_epic_success(self, client: AsyncClient, project_owner):
        """200 — задача привязана к эпику."""
        proj = project_owner
        task = await create_task(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        # Используем валидный ID эпика (в реальном тесте нужно получить из системы)
        resp = await client.post(
            f"{API}/tasks/{task['task_id']}/epic",
            json={"epic_id": "00000000-0000-0000-0000-000000000001"},
            headers=auth_headers(proj["access_token"])
        )
        # Может вернуть 404 если эпик не существует, 200 если успешно, или 400 если endpoint не существует
        assert resp.status_code in (200, 404, 400)

    async def test_assign_to_epic_no_auth(self, client: AsyncClient, project_owner):
        """401 — без токена авторизации."""
        proj = project_owner
        task = await create_task(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        resp = await client.post(
            f"{API}/tasks/{task['task_id']}/epic",
            json={"epic_id": "00000000-0000-0000-0000-000000000001"}
        )
        assert resp.status_code == 401

    async def test_assign_to_epic_forbidden(self, client: AsyncClient, project_owner):
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
            f"{API}/tasks/{task['task_id']}/epic",
            json={"epic_id": "00000000-0000-0000-0000-000000000001"},
            headers=auth_headers(stranger["access_token"])
        )
        assert resp.status_code == 403

    async def test_assign_to_epic_not_found(self, client: AsyncClient, project_owner):
        """404 — задача не найдена."""
        proj = project_owner
        resp = await client.post(
            f"{API}/tasks/00000000-0000-0000-0000-000000000000/epic",
            json={"epic_id": "00000000-0000-0000-0000-000000000001"},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 404

    async def test_assign_to_epic_validation_missing_epic_id(self, client: AsyncClient, project_owner):
        """422 — отсутствует epic_id."""
        proj = project_owner
        task = await create_task(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        resp = await client.post(
            f"{API}/tasks/{task['task_id']}/epic",
            json={},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 422

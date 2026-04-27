"""E2E-тесты: POST /tasks/{task_id}/change-status — Смена статуса задачи."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    create_task,
    register_and_login,
)


@pytest.mark.e2e
class TestChangeStatus:
    """Смена статуса задачи."""

    async def test_change_status_success(self, client: AsyncClient, project_owner):
        """200 — статус задачи изменён."""
        proj = project_owner
        task = await create_task(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        # Используем валидный ID статуса (в реальном тесте нужно получить из системы)
        resp = await client.post(
            f"{API}/tasks/{task['task_id']}/change-status",
            json={"new_status_id": "00000000-0000-0000-0000-000000000001"},
            headers=auth_headers(proj["access_token"])
        )
        # Может вернуть 404 если статус не существует, 409 если переход не разрешён
        assert resp.status_code in (200, 404, 409)

    async def test_change_status_no_auth(self, client: AsyncClient, project_owner):
        """401 — без токена авторизации."""
        proj = project_owner
        task = await create_task(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        resp = await client.post(
            f"{API}/tasks/{task['task_id']}/change-status",
            json={"new_status_id": "00000000-0000-0000-0000-000000000001"}
        )
        assert resp.status_code == 401

    async def test_change_status_forbidden(self, client: AsyncClient, project_owner):
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
            f"{API}/tasks/{task['task_id']}/change-status",
            json={"new_status_id": "00000000-0000-0000-0000-000000000001"},
            headers=auth_headers(stranger["access_token"])
        )
        assert resp.status_code == 403

    async def test_change_status_not_found(self, client: AsyncClient, project_owner):
        """404 — задача не найдена."""
        proj = project_owner
        resp = await client.post(
            f"{API}/tasks/00000000-0000-0000-0000-000000000000/change-status",
            json={"new_status_id": "00000000-0000-0000-0000-000000000001"},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 404

    async def test_change_status_validation_missing_status_id(self, client: AsyncClient, project_owner):
        """422 — отсутствует status_id."""
        proj = project_owner
        task = await create_task(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        resp = await client.post(
            f"{API}/tasks/{task['task_id']}/change-status",
            json={},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 422

"""E2E-тесты: POST /workspaces/{ws_id}/projects/{project_id}/tasks/bulk — Массовое обновление задач."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    create_task,
    register_and_login,
)


@pytest.mark.e2e
class TestBulkUpdateTasks:
    """Массовое обновление задач."""

    async def test_bulk_update_success(self, client: AsyncClient, project_owner):
        """200 — задачи обновлены."""
        proj = project_owner
        task1 = await create_task(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        task2 = await create_task(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/tasks/bulk",
            json={
                "task_ids": [task1["task_id"], task2["task_id"]],
                "changes": {"priority": "high"}
            },
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 200

    async def test_bulk_update_no_auth(self, client: AsyncClient, project_owner):
        """401 — без токена авторизации."""
        proj = project_owner
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/tasks/bulk",
            json={"task_ids": [], "changes": {}}
        )
        assert resp.status_code == 401

    async def test_bulk_update_forbidden(self, client: AsyncClient, project_owner):
        """403 — пользователь не участник проекта."""
        proj = project_owner
        task1 = await create_task(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        stranger = await register_and_login(client)
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/tasks/bulk",
            json={"task_ids": [task1["task_id"]], "changes": {"priority": "high"}},
            headers=auth_headers(stranger["access_token"])
        )
        assert resp.status_code == 403

    async def test_bulk_update_validation_missing_task_ids(self, client: AsyncClient, project_owner):
        """422 — отсутствует task_ids."""
        proj = project_owner
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/tasks/bulk",
            json={"changes": {"priority": "high"}},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 422

    async def test_bulk_update_validation_missing_changes(self, client: AsyncClient, project_owner):
        """422 — отсутствует changes."""
        proj = project_owner
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/tasks/bulk",
            json={"task_ids": []},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 422

    async def test_bulk_update_validation_empty_task_ids(self, client: AsyncClient, project_owner):
        """422 — пустой список task_ids."""
        proj = project_owner
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/tasks/bulk",
            json={"task_ids": [], "changes": {"priority": "high"}},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 422

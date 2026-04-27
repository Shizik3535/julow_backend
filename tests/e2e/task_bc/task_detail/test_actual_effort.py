"""E2E-тесты: PATCH /tasks/{task_id}/actual-effort — Установка фактических усилий."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    create_task,
    register_and_login,
)


@pytest.mark.e2e
class TestActualEffort:
    """Установка фактических усилий."""

    async def test_set_actual_effort_success(self, client: AsyncClient, project_owner):
        """200 — фактические усилия установлены."""
        proj = project_owner
        task = await create_task(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        resp = await client.patch(
            f"{API}/tasks/{task['task_id']}/actual-effort",
            json={"value": 5, "unit": "hours"},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 200

    async def test_set_actual_effort_no_auth(self, client: AsyncClient, project_owner):
        """401 — без токена авторизации."""
        proj = project_owner
        task = await create_task(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        resp = await client.patch(
            f"{API}/tasks/{task['task_id']}/actual-effort",
            json={"value": 5, "unit": "hours"}
        )
        assert resp.status_code == 401

    async def test_set_actual_effort_forbidden(self, client: AsyncClient, project_owner):
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
            f"{API}/tasks/{task['task_id']}/actual-effort",
            json={"value": 5, "unit": "hours"},
            headers=auth_headers(stranger["access_token"])
        )
        assert resp.status_code == 403

    async def test_set_actual_effort_not_found(self, client: AsyncClient, project_owner):
        """404 — задача не найдена."""
        proj = project_owner
        resp = await client.patch(
            f"{API}/tasks/00000000-0000-0000-0000-000000000000/actual-effort",
            json={"value": 5, "unit": "hours"},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 404

    async def test_set_actual_effort_validation_missing_value(self, client: AsyncClient, project_owner):
        """422 — отсутствует value."""
        proj = project_owner
        task = await create_task(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        resp = await client.patch(
            f"{API}/tasks/{task['task_id']}/actual-effort",
            json={"unit": "hours"},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 422

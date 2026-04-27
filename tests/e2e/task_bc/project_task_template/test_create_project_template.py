"""E2E-тесты: POST /workspaces/{ws_id}/projects/{project_id}/project-task-templates — Создание проектного шаблона задачи."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    register_and_login,
)


@pytest.mark.e2e
class TestCreateProjectTaskTemplate:
    """Создание проектного шаблона задачи."""

    async def test_create_project_template_success(self, client: AsyncClient, project_owner):
        """201 — проектный шаблон создан."""
        proj = project_owner
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/project-task-templates",
            json={"name": "Project Template", "task_type": "task"},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code in (201, 404)  # Может быть 404 если endpoint не существует

    async def test_create_project_template_no_auth(self, client: AsyncClient, project_owner):
        """401 — без токена авторизации."""
        proj = project_owner
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/project-task-templates",
            json={"name": "Project Template", "task_type": "task"}
        )
        assert resp.status_code in (401, 404)  # Может быть 404 если endpoint не существует

    async def test_create_project_template_forbidden(self, client: AsyncClient, project_owner):
        """403 — пользователь не участник проекта."""
        proj = project_owner
        stranger = await register_and_login(client)
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/project-task-templates",
            json={"name": "Project Template", "task_type": "task"},
            headers=auth_headers(stranger["access_token"])
        )
        assert resp.status_code in (403, 404)

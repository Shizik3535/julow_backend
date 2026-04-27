"""E2E-тесты: POST /workspaces/{ws_id}/projects/{project_id}/task-templates — Создание шаблона задачи."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    create_task_template,
    register_and_login,
)


@pytest.mark.e2e
class TestCreateTaskTemplate:
    """Создание шаблона задачи."""

    async def test_create_template_success(self, client: AsyncClient, project_owner):
        """201 — шаблон создан."""
        proj = project_owner
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/task-templates",
            json={"name": "Test Template", "task_type": "task"},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 201
        data = resp.json()["data"]
        assert data["id"]
        assert data["name"] == "Test Template"

    async def test_create_template_no_auth(self, client: AsyncClient, project_owner):
        """401 — без токена авторизации."""
        proj = project_owner
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/task-templates",
            json={"name": "Test Template", "task_type": "task"}
        )
        assert resp.status_code == 401

    async def test_create_template_forbidden(self, client: AsyncClient, project_owner):
        """403 — пользователь не участник проекта."""
        proj = project_owner
        stranger = await register_and_login(client)
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/task-templates",
            json={"name": "Test Template", "task_type": "task"},
            headers=auth_headers(stranger["access_token"])
        )
        assert resp.status_code == 403

    async def test_create_template_validation_missing_name(self, client: AsyncClient, project_owner):
        """422 — отсутствует name."""
        proj = project_owner
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/task-templates",
            json={"task_type": "task"},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 422

    async def test_create_template_validation_empty_name(self, client: AsyncClient, project_owner):
        """422 — пустой name."""
        proj = project_owner
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/task-templates",
            json={"name": "", "task_type": "task"},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 422

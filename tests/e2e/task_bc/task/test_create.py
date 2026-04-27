"""E2E-тесты: POST /workspaces/{ws_id}/projects/{project_id}/tasks — Создание задачи."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    create_project,
    register_and_login,
)


@pytest.mark.e2e
class TestCreateTask:
    """Создание задачи."""

    async def test_create_success(self, client: AsyncClient, project_owner):
        """201 — задача создана."""
        proj = project_owner
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/tasks",
            json={"title": "Test Task", "task_type": "task"},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 201
        data = resp.json()["data"]
        assert data["id"]
        assert data["title"] == "Test Task"
        assert data["task_type"] == "task"

    async def test_create_with_bug_type(self, client: AsyncClient, project_owner):
        """201 — задача с типом bug."""
        proj = project_owner
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/tasks",
            json={"title": "Bug Task", "task_type": "bug"},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 201
        data = resp.json()["data"]
        assert data["task_type"] == "bug"

    async def test_create_with_story_type(self, client: AsyncClient, project_owner):
        """201 — задача с типом story."""
        proj = project_owner
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/tasks",
            json={"title": "Story Task", "task_type": "story"},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 201
        data = resp.json()["data"]
        assert data["task_type"] == "story"

    async def test_create_no_auth(self, client: AsyncClient, project_owner):
        """401 — без токена авторизации."""
        proj = project_owner
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/tasks",
            json={"title": "NoAuth Task", "task_type": "task"}
        )
        assert resp.status_code == 401

    async def test_create_forbidden_non_project_member(self, client: AsyncClient, project_owner):
        """403 — пользователь не участник проекта."""
        proj = project_owner
        stranger = await register_and_login(client)
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/tasks",
            json={"title": "Forbidden Task", "task_type": "task"},
            headers=auth_headers(stranger["access_token"])
        )
        assert resp.status_code == 403

    async def test_create_validation_missing_title(self, client: AsyncClient, project_owner):
        """422 — отсутствует title."""
        proj = project_owner
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/tasks",
            json={"task_type": "task"},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 422

    async def test_create_validation_empty_title(self, client: AsyncClient, project_owner):
        """422 — пустой title."""
        proj = project_owner
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/tasks",
            json={"title": "", "task_type": "task"},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 422

    async def test_create_validation_missing_body(self, client: AsyncClient, project_owner):
        """422 — отсутствует тело запроса."""
        proj = project_owner
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/tasks",
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 422

    async def test_create_project_not_found(self, client: AsyncClient, project_owner):
        """404 — проект не найден."""
        proj = project_owner
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/00000000-0000-0000-0000-000000000000/tasks",
            json={"title": "NotFound Task", "task_type": "task"},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code in (404, 400)  # 400 if project UUID validation fails

"""E2E-тесты: POST /workspaces/{ws_id}/projects/{project_id}/tasks/from-template — Создание задачи из шаблона."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    create_task_template,
    register_and_login,
)


@pytest.mark.e2e
class TestCreateTaskFromTemplate:
    """Создание задачи из шаблона."""

    async def test_create_from_template_success(self, client: AsyncClient, project_owner):
        """201 — задача создана из шаблона."""
        proj = project_owner
        template = await create_task_template(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"],
            name="Test Template"
        )
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/tasks/from-template",
            json={"template_id": template["template_id"], "reporter_id": proj["user_id"]},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 201
        data = resp.json()["data"]
        assert data["id"]
        assert data["task_type"] == "task"

    async def test_create_from_template_no_auth(self, client: AsyncClient, project_owner):
        """401 — без токена авторизации."""
        proj = project_owner
        template = await create_task_template(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/tasks/from-template",
            json={"template_id": template["template_id"], "reporter_id": proj["user_id"]}
        )
        assert resp.status_code == 401

    async def test_create_from_template_forbidden(self, client: AsyncClient, project_owner):
        """403 — пользователь не участник проекта."""
        proj = project_owner
        template = await create_task_template(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        stranger = await register_and_login(client)
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/tasks/from-template",
            json={"template_id": template["template_id"], "reporter_id": stranger["user_id"]},
            headers=auth_headers(stranger["access_token"])
        )
        assert resp.status_code == 403

    async def test_create_from_template_not_found(self, client: AsyncClient, project_owner):
        """404 — шаблон не найден."""
        proj = project_owner
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/tasks/from-template",
            json={"template_id": "00000000-0000-0000-0000-000000000000", "reporter_id": proj["user_id"]},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 404

    async def test_create_from_template_validation_missing_template_id(self, client: AsyncClient, project_owner):
        """422 — отсутствует template_id."""
        proj = project_owner
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/tasks/from-template",
            json={},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 422

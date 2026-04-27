"""E2E-тесты: GET /workspaces/{ws_id}/projects/{project_id}/task-templates — Список шаблонов задач."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    create_task_template,
    register_and_login,
)


@pytest.mark.e2e
class TestListTaskTemplates:
    """Список шаблонов задач."""

    async def test_list_templates_success(self, client: AsyncClient, project_owner):
        """200 — список шаблонов получен."""
        proj = project_owner
        await create_task_template(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        resp = await client.get(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/task-templates",
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "total" in data

    async def test_list_templates_empty(self, client: AsyncClient, project_owner):
        """200 — пустой список шаблонов."""
        proj = project_owner
        resp = await client.get(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/task-templates",
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0

    async def test_list_templates_no_auth(self, client: AsyncClient, project_owner):
        """401 — без токена авторизации."""
        proj = project_owner
        resp = await client.get(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/task-templates"
        )
        assert resp.status_code == 401

    async def test_list_templates_forbidden(self, client: AsyncClient, project_owner):
        """403 — пользователь не участник проекта."""
        proj = project_owner
        stranger = await register_and_login(client)
        resp = await client.get(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/task-templates",
            headers=auth_headers(stranger["access_token"])
        )
        assert resp.status_code == 403

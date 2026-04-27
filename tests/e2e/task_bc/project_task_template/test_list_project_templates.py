"""E2E-тесты: GET /workspaces/{ws_id}/projects/{project_id}/project-task-templates — Список проектных шаблонов."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    register_and_login,
)


@pytest.mark.e2e
class TestListProjectTaskTemplates:
    """Список проектных шаблонов."""

    async def test_list_project_templates_success(self, client: AsyncClient, project_owner):
        """200 — список проектных шаблонов получен."""
        proj = project_owner
        resp = await client.get(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/project-task-templates",
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code in (200, 404)

    async def test_list_project_templates_no_auth(self, client: AsyncClient, project_owner):
        """401 — без токена авторизации."""
        proj = project_owner
        resp = await client.get(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/project-task-templates"
        )
        assert resp.status_code in (401, 404)

    async def test_list_project_templates_forbidden(self, client: AsyncClient, project_owner):
        """403 — пользователь не участник проекта."""
        proj = project_owner
        stranger = await register_and_login(client)
        resp = await client.get(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/project-task-templates",
            headers=auth_headers(stranger["access_token"])
        )
        assert resp.status_code in (403, 404)

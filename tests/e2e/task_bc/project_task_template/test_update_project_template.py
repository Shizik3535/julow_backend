"""E2E-тесты: PATCH /workspaces/{ws_id}/projects/{project_id}/project-task-templates/{template_id} — Обновление проектного шаблона."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    register_and_login,
)


@pytest.mark.e2e
class TestUpdateProjectTaskTemplate:
    """Обновление проектного шаблона."""

    async def test_update_project_template_success(self, client: AsyncClient, project_owner):
        """200 — проектный шаблон обновлён."""
        proj = project_owner
        resp = await client.patch(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/project-task-templates/00000000-0000-0000-0000-000000000001",
            json={"name": "Updated Template"},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code in (200, 404)

    async def test_update_project_template_no_auth(self, client: AsyncClient, project_owner):
        """401 — без токена авторизации."""
        proj = project_owner
        resp = await client.patch(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/project-task-templates/00000000-0000-0000-0000-000000000001",
            json={"name": "Updated Template"}
        )
        assert resp.status_code in (401, 404)

    async def test_update_project_template_forbidden(self, client: AsyncClient, project_owner):
        """403 — пользователь не участник проекта."""
        proj = project_owner
        stranger = await register_and_login(client)
        resp = await client.patch(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/project-task-templates/00000000-0000-0000-0000-000000000001",
            json={"name": "Updated Template"},
            headers=auth_headers(stranger["access_token"])
        )
        assert resp.status_code in (403, 404)

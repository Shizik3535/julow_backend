"""E2E-тесты: PATCH /workspaces/{ws_id}/projects/{project_id}/task-templates/{template_id} — Обновление шаблона задачи."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    create_task_template,
    register_and_login,
)


@pytest.mark.e2e
class TestUpdateTaskTemplate:
    """Обновление шаблона задачи."""

    async def test_update_template_success(self, client: AsyncClient, project_owner):
        """200 — шаблон обновлён."""
        proj = project_owner
        template = await create_task_template(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        resp = await client.patch(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/task-templates/{template['template_id']}",
            json={"name": "Updated Template"},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 200

    async def test_update_template_no_auth(self, client: AsyncClient, project_owner):
        """401 — без токена авторизации."""
        proj = project_owner
        template = await create_task_template(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        resp = await client.patch(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/task-templates/{template['template_id']}",
            json={"name": "Updated Template"}
        )
        assert resp.status_code == 401

    async def test_update_template_forbidden(self, client: AsyncClient, project_owner):
        """403 — пользователь не участник проекта."""
        proj = project_owner
        template = await create_task_template(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        stranger = await register_and_login(client)
        resp = await client.patch(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/task-templates/{template['template_id']}",
            json={"name": "Updated Template"},
            headers=auth_headers(stranger["access_token"])
        )
        assert resp.status_code == 403

    async def test_update_template_not_found(self, client: AsyncClient, project_owner):
        """404 — шаблон не найден."""
        proj = project_owner
        resp = await client.patch(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/task-templates/00000000-0000-0000-0000-000000000000",
            json={"name": "Updated Template"},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 404

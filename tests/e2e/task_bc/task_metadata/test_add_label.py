"""E2E-тесты: POST /tasks/{task_id}/labels — Добавление метки к задаче."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    create_task,
    register_and_login,
)


@pytest.mark.e2e
class TestAddLabel:
    """Добавление метки к задаче."""

    async def test_add_label_success(self, client: AsyncClient, project_owner):
        """200 — метка добавлена."""
        proj = project_owner
        task = await create_task(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        resp = await client.post(
            f"{API}/tasks/{task['task_id']}/labels",
            json={"name": "bug", "color": "#FF0000"},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 200

    async def test_add_label_no_auth(self, client: AsyncClient, project_owner):
        """401 — без токена авторизации."""
        proj = project_owner
        task = await create_task(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        resp = await client.post(
            f"{API}/tasks/{task['task_id']}/labels",
            json={"name": "bug", "color": "#FF0000"}
        )
        assert resp.status_code == 401

    async def test_add_label_forbidden(self, client: AsyncClient, project_owner):
        """403 — пользователь не участник проекта."""
        proj = project_owner
        task = await create_task(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        stranger = await register_and_login(client)
        resp = await client.post(
            f"{API}/tasks/{task['task_id']}/labels",
            json={"name": "bug", "color": "#FF0000"},
            headers=auth_headers(stranger["access_token"])
        )
        assert resp.status_code == 403

    async def test_add_label_not_found(self, client: AsyncClient, project_owner):
        """404 — задача не найдена."""
        proj = project_owner
        resp = await client.post(
            f"{API}/tasks/00000000-0000-0000-0000-000000000000/labels",
            json={"name": "bug", "color": "#FF0000"},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 404

    async def test_add_label_validation_missing_name(self, client: AsyncClient, project_owner):
        """422 — отсутствует name."""
        proj = project_owner
        task = await create_task(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        resp = await client.post(
            f"{API}/tasks/{task['task_id']}/labels",
            json={},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 422

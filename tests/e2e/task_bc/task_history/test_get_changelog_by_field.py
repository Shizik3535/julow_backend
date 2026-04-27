"""E2E-тесты: GET /tasks/{task_id}/changelog/{field} — Получение истории изменений по полю."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    create_task,
    register_and_login,
)


@pytest.mark.e2e
class TestGetChangelogByField:
    """Получение истории изменений по полю."""

    async def test_get_changelog_by_field_success(self, client: AsyncClient, project_owner):
        """200 — история изменений по полю получена."""
        proj = project_owner
        task = await create_task(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        # Вносим изменение в title
        await client.patch(
            f"{API}/tasks/{task['task_id']}",
            json={"title": "Updated Title"},
            headers=auth_headers(proj["access_token"])
        )
        resp = await client.get(
            f"{API}/tasks/{task['task_id']}/changelog/title",
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data

    async def test_get_changelog_by_field_no_auth(self, client: AsyncClient, project_owner):
        """401 — без токена авторизации."""
        proj = project_owner
        task = await create_task(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        resp = await client.get(f"{API}/tasks/{task['task_id']}/changelog/title")
        assert resp.status_code == 401

    async def test_get_changelog_by_field_forbidden(self, client: AsyncClient, project_owner):
        """403 — пользователь не участник проекта."""
        proj = project_owner
        task = await create_task(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        stranger = await register_and_login(client)
        resp = await client.get(
            f"{API}/tasks/{task['task_id']}/changelog/title",
            headers=auth_headers(stranger["access_token"])
        )
        assert resp.status_code == 403

    async def test_get_changelog_by_field_not_found(self, client: AsyncClient, project_owner):
        """404 — задача не найдена."""
        proj = project_owner
        resp = await client.get(
            f"{API}/tasks/00000000-0000-0000-0000-000000000000/changelog/title",
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 404

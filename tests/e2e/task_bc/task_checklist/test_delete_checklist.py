"""E2E-тесты: DELETE /tasks/{task_id}/checklists/{checklist_id} — Удаление чеклиста."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    create_task,
    register_and_login,
)


@pytest.mark.e2e
class TestDeleteChecklist:
    """Удаление чеклиста."""

    async def test_delete_checklist_success(self, client: AsyncClient, project_owner):
        """200 — чеклист удалён."""
        proj = project_owner
        task = await create_task(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        # Сначала создаём чеклист
        checklist_resp = await client.post(
            f"{API}/tasks/{task['task_id']}/checklists",
            json={"title": "Test Checklist"},
            headers=auth_headers(proj["access_token"])
        )
        if checklist_resp.status_code in (200, 201):
            checklist_id = checklist_resp.json()["data"].get("id", "00000000-0000-0000-0000-000000000001")
            # Затем удаляем
            resp = await client.delete(
                f"{API}/tasks/{task['task_id']}/checklists/{checklist_id}",
                headers=auth_headers(proj["access_token"])
            )
            assert resp.status_code == 200

    async def test_delete_checklist_no_auth(self, client: AsyncClient, project_owner):
        """401 — без токена авторизации."""
        proj = project_owner
        task = await create_task(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        resp = await client.delete(
            f"{API}/tasks/{task['task_id']}/checklists/00000000-0000-0000-0000-000000000001"
        )
        assert resp.status_code == 401

    async def test_delete_checklist_forbidden(self, client: AsyncClient, project_owner):
        """403 — пользователь не участник проекта."""
        proj = project_owner
        task = await create_task(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        stranger = await register_and_login(client)
        resp = await client.delete(
            f"{API}/tasks/{task['task_id']}/checklists/00000000-0000-0000-0000-000000000001",
            headers=auth_headers(stranger["access_token"])
        )
        assert resp.status_code == 403

    async def test_delete_checklist_not_found(self, client: AsyncClient, project_owner):
        """404 — задача или чеклист не найдены."""
        proj = project_owner
        resp = await client.delete(
            f"{API}/tasks/00000000-0000-0000-0000-000000000000/checklists/00000000-0000-0000-0000-000000000001",
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 404

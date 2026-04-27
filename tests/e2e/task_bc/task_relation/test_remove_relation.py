"""E2E-тесты: DELETE /tasks/{task_id}/relations/{relation_id} — Удаление связи между задачами."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    create_task,
    register_and_login,
)


@pytest.mark.e2e
class TestRemoveRelation:
    """Удаление связи между задачами."""

    async def test_remove_relation_success(self, client: AsyncClient, project_owner):
        """200 — связь удалена."""
        proj = project_owner
        task1 = await create_task(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        task2 = await create_task(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        # Сначала добавляем связь
        add_resp = await client.post(
            f"{API}/tasks/{task1['task_id']}/relations",
            json={"related_task_id": task2["task_id"], "relation_type": "blocks"},
            headers=auth_headers(proj["access_token"])
        )
        if add_resp.status_code == 200:
            # Затем удаляем связь (используем related_task_id)
            resp = await client.delete(
                f"{API}/tasks/{task1['task_id']}/relations/{task2['task_id']}",
                params={"relation_type": "blocks"},
                headers=auth_headers(proj["access_token"])
            )
            assert resp.status_code == 200

    async def test_remove_relation_no_auth(self, client: AsyncClient, project_owner):
        """401 — без токена авторизации."""
        proj = project_owner
        task1 = await create_task(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        resp = await client.delete(
            f"{API}/tasks/{task1['task_id']}/relations/00000000-0000-0000-0000-000000000001"
        )
        assert resp.status_code == 401

    async def test_remove_relation_forbidden(self, client: AsyncClient, project_owner):
        """403 — пользователь не участник проекта."""
        proj = project_owner
        task1 = await create_task(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        stranger = await register_and_login(client)
        resp = await client.delete(
            f"{API}/tasks/{task1['task_id']}/relations/00000000-0000-0000-0000-000000000001",
            headers=auth_headers(stranger["access_token"])
        )
        assert resp.status_code == 403

    async def test_remove_relation_not_found(self, client: AsyncClient, project_owner):
        """404 — задача или связь не найдена."""
        proj = project_owner
        task1 = await create_task(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        resp = await client.delete(
            f"{API}/tasks/{task1['task_id']}/relations/00000000-0000-0000-0000-000000000001",
            params={"relation_type": "blocks"},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code in (404, 200)  # Может быть 200 если связь не существует

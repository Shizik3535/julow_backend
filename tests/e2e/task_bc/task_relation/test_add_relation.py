"""E2E-тесты: POST /tasks/{task_id}/relations — Добавление связи между задачами."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    create_task,
    register_and_login,
)


@pytest.mark.e2e
class TestAddRelation:
    """Добавление связи между задачами."""

    async def test_add_relation_blocks(self, client: AsyncClient, project_owner):
        """200 — связь типа 'blocks' добавлена."""
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
        resp = await client.post(
            f"{API}/tasks/{task1['task_id']}/relations",
            json={"related_task_id": task2["task_id"], "relation_type": "blocks"},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 200

    async def test_add_relation_is_blocked_by(self, client: AsyncClient, project_owner):
        """200 — связь типа 'is_blocked_by' добавлена."""
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
        resp = await client.post(
            f"{API}/tasks/{task1['task_id']}/relations",
            json={"related_task_id": task2["task_id"], "relation_type": "is_blocked_by"},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 200

    async def test_add_relation_relates_to(self, client: AsyncClient, project_owner):
        """200 — связь типа 'relates_to' добавлена."""
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
        resp = await client.post(
            f"{API}/tasks/{task1['task_id']}/relations",
            json={"related_task_id": task2["task_id"], "relation_type": "relates_to"},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 200

    async def test_add_relation_no_auth(self, client: AsyncClient, project_owner):
        """401 — без токена авторизации."""
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
        resp = await client.post(
            f"{API}/tasks/{task1['task_id']}/relations",
            json={"related_task_id": task2["task_id"], "relation_type": "blocks"}
        )
        assert resp.status_code == 401

    async def test_add_relation_forbidden(self, client: AsyncClient, project_owner):
        """403 — пользователь не участник проекта."""
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
        stranger = await register_and_login(client)
        resp = await client.post(
            f"{API}/tasks/{task1['task_id']}/relations",
            json={"related_task_id": task2["task_id"], "relation_type": "blocks"},
            headers=auth_headers(stranger["access_token"])
        )
        assert resp.status_code == 403

    async def test_add_relation_not_found(self, client: AsyncClient, project_owner):
        """404 — задача не найдена."""
        proj = project_owner
        task2 = await create_task(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        resp = await client.post(
            f"{API}/tasks/00000000-0000-0000-0000-000000000000/relations",
            json={"related_task_id": task2["task_id"], "relation_type": "blocks"},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 404

    async def test_add_relation_validation_missing_related_task_id(self, client: AsyncClient, project_owner):
        """422 — отсутствует related_task_id."""
        proj = project_owner
        task1 = await create_task(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        resp = await client.post(
            f"{API}/tasks/{task1['task_id']}/relations",
            json={"relation_type": "blocks"},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 422

    async def test_add_relation_validation_missing_relation_type(self, client: AsyncClient, project_owner):
        """422 — отсутствует relation_type."""
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
        resp = await client.post(
            f"{API}/tasks/{task1['task_id']}/relations",
            json={"related_task_id": task2["task_id"]},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 422

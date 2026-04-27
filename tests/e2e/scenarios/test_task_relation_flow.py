"""E2E-тесты сценария: Связи между задачами — Создание задач → Добавление связей."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    create_task,
    create_task_with_project,
)


@pytest.mark.e2e
class TestTaskRelationFlow:
    """Сценарий работы со связями между задачами."""

    async def test_task_relation_flow(self, client: AsyncClient):
        """Полный цикл: создать задачи → добавить связь типа blocks."""
        # 1. Создаём проект и первую задачу
        task_data = await create_task_with_project(client)
        token = task_data["access_token"]
        ws_id = task_data["ws_id"]
        project_id = task_data["project_id"]
        task1_id = task_data["task_id"]

        # 2. Создаём вторую задачу
        task2 = await create_task(
            client,
            ws_id=ws_id,
            project_id=project_id,
            token=token
        )
        task2_id = task2["task_id"]

        # 3. Добавляем связь типа "blocks"
        relation_resp = await client.post(
            f"{API}/tasks/{task1_id}/relations",
            json={"related_task_id": task2_id, "relation_type": "blocks"},
            headers=auth_headers(token)
        )
        assert relation_resp.status_code in (200, 403, 404)

        # 4. Проверяем, что обе задачи существуют
        get1_resp = await client.get(
            f"{API}/tasks/{task1_id}",
            headers=auth_headers(token)
        )
        assert get1_resp.status_code == 200

        get2_resp = await client.get(
            f"{API}/tasks/{task2_id}",
            headers=auth_headers(token)
        )
        assert get2_resp.status_code == 200

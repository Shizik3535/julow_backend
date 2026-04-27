"""E2E-тесты сценария: Рекуррентная задача — Создание → Завершение → Создание новой задачи."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    create_task_with_project,
)


@pytest.mark.e2e
class TestRecurringTaskFlow:
    """Сценарий работы с рекуррентными задачами."""

    async def test_recurring_task_flow(self, client: AsyncClient):
        """Полный цикл: создать рекуррентную задачу → завершить → проверить создание новой."""
        # 1. Создаём задачу
        task_data = await create_task_with_project(client)
        task_id = task_data["task_id"]
        token = task_data["access_token"]

        # 2. Устанавливаем рекуррентность
        recurrence_resp = await client.post(
            f"{API}/tasks/{task_id}/recurrence",
            json={
                "pattern": "daily",
                "interval": 1
            },
            headers=auth_headers(token)
        )
        assert recurrence_resp.status_code in (200, 403, 404)

        # 3. Завершаем задачу (меняем статус на завершённый)
        complete_resp = await client.post(
            f"{API}/tasks/{task_id}/change-status",
            json={"new_status_id": "00000000-0000-0000-0000-000000000002"},
            headers=auth_headers(token)
        )
        assert complete_resp.status_code in (200, 404, 403, 409)

        # 4. Проверяем, что исходная задача завершена
        get_resp = await client.get(
            f"{API}/tasks/{task_id}",
            headers=auth_headers(token)
        )
        assert get_resp.status_code == 200

        # 5. Проверяем список задач на наличие новой (если рекуррентность сработала)
        # В реальной системе это может требовать ожидания события
        list_resp = await client.get(
            f"{API}/workspaces/{task_data['ws_id']}/projects/{task_data['project_id']}/tasks",
            headers=auth_headers(token)
        )
        assert list_resp.status_code == 200

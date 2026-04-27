"""E2E-тесты сценария: Задача с чеклистом — Создание → Добавление чеклиста → Выполнение элементов."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    create_task_with_project,
)


@pytest.mark.e2e
class TestTaskWithChecklistFlow:
    """Сценарий работы с чеклистом."""

    async def test_task_with_checklist_flow(self, client: AsyncClient):
        """Полный цикл: создать задачу → добавить чеклист → выполнить элементы."""
        # 1. Создаём задачу
        task_data = await create_task_with_project(client)
        task_id = task_data["task_id"]
        token = task_data["access_token"]

        # 2. Создаём чеклист
        checklist_resp = await client.post(
            f"{API}/tasks/{task_id}/checklists",
            json={"title": "Test Checklist"},
            headers=auth_headers(token)
        )
        assert checklist_resp.status_code == 201

        checklist_id = checklist_resp.json()["data"].get("id", "00000000-0000-0000-0000-000000000001")

        # 3. Добавляем элементы в чеклист
        item1_resp = await client.post(
            f"{API}/tasks/{task_id}/checklists/{checklist_id}/items",
            json={"text": "Item 1"},
            headers=auth_headers(token)
        )
        assert item1_resp.status_code == 200

        item_id = item1_resp.json()["data"].get("id", "00000000-0000-0000-0000-000000000001")

        # 4. Отмечаем элемент как выполненный (toggle)
        update_resp = await client.post(
            f"{API}/tasks/{task_id}/checklists/{checklist_id}/items/{item_id}/toggle",
            headers=auth_headers(token)
        )
        assert update_resp.status_code == 200

        # 5. Проверяем, что задача существует
        get_resp = await client.get(
            f"{API}/tasks/{task_id}",
            headers=auth_headers(token)
        )
        assert get_resp.status_code == 200

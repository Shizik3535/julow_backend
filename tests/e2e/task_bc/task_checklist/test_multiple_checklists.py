"""E2E-тесты: Множественные чеклисты — Создание нескольких чеклистов, добавление элементов, toggle, удаление."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    create_task,
    register_and_login,
)


def _extract_id(resp) -> str:
    """Извлечь id из ответа."""
    return resp.json()["data"].get("id", "00000000-0000-0000-0000-000000000001")


@pytest.mark.e2e
class TestMultipleChecklists:
    """Сценарии работы с несколькими чеклистами на одной задаче."""

    async def test_create_multiple_checklists_on_task(self, client: AsyncClient, project_owner):
        """200 — можно создать несколько чеклистов на одну задачу."""
        proj = project_owner
        task = await create_task(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        headers = auth_headers(proj["access_token"])

        cl1_resp = await client.post(
            f"{API}/tasks/{task['task_id']}/checklists",
            json={"title": "Checklist 1"},
            headers=headers,
        )
        assert cl1_resp.status_code == 201
        cl1_id = _extract_id(cl1_resp)

        cl2_resp = await client.post(
            f"{API}/tasks/{task['task_id']}/checklists",
            json={"title": "Checklist 2"},
            headers=headers,
        )
        assert cl2_resp.status_code == 201
        cl2_id = _extract_id(cl2_resp)

        # Разные id
        assert cl1_id != cl2_id

    async def test_add_items_to_different_checklists(self, client: AsyncClient, project_owner):
        """200 — элементы добавляются в разные чеклисты независимо."""
        proj = project_owner
        task = await create_task(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        headers = auth_headers(proj["access_token"])

        # Создаём два чеклиста
        cl1_resp = await client.post(
            f"{API}/tasks/{task['task_id']}/checklists",
            json={"title": "First"},
            headers=headers,
        )
        assert cl1_resp.status_code == 201
        cl1_id = _extract_id(cl1_resp)

        cl2_resp = await client.post(
            f"{API}/tasks/{task['task_id']}/checklists",
            json={"title": "Second"},
            headers=headers,
        )
        assert cl2_resp.status_code == 201
        cl2_id = _extract_id(cl2_resp)

        # Добавляем элементы в первый чеклист
        item1_resp = await client.post(
            f"{API}/tasks/{task['task_id']}/checklists/{cl1_id}/items",
            json={"text": "Item A1"},
            headers=headers,
        )
        assert item1_resp.status_code == 201

        item2_resp = await client.post(
            f"{API}/tasks/{task['task_id']}/checklists/{cl1_id}/items",
            json={"text": "Item A2"},
            headers=headers,
        )
        assert item2_resp.status_code == 201

        # Добавляем элементы во второй чеклист
        item3_resp = await client.post(
            f"{API}/tasks/{task['task_id']}/checklists/{cl2_id}/items",
            json={"text": "Item B1"},
            headers=headers,
        )
        assert item3_resp.status_code == 201

    async def test_toggle_items_in_different_checklists(self, client: AsyncClient, project_owner):
        """200 — toggle элементов в разных чеклистах не влияет друг на друга."""
        proj = project_owner
        task = await create_task(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        headers = auth_headers(proj["access_token"])

        # Создаём два чеклиста с элементами
        cl1_resp = await client.post(
            f"{API}/tasks/{task['task_id']}/checklists",
            json={"title": "CL-1"},
            headers=headers,
        )
        assert cl1_resp.status_code == 201
        cl1_id = _extract_id(cl1_resp)

        cl2_resp = await client.post(
            f"{API}/tasks/{task['task_id']}/checklists",
            json={"title": "CL-2"},
            headers=headers,
        )
        assert cl2_resp.status_code == 201
        cl2_id = _extract_id(cl2_resp)

        item1_resp = await client.post(
            f"{API}/tasks/{task['task_id']}/checklists/{cl1_id}/items",
            json={"text": "Item 1"},
            headers=headers,
        )
        assert item1_resp.status_code == 201
        item1_id = _extract_id(item1_resp)

        item2_resp = await client.post(
            f"{API}/tasks/{task['task_id']}/checklists/{cl2_id}/items",
            json={"text": "Item 2"},
            headers=headers,
        )
        assert item2_resp.status_code == 201
        item2_id = _extract_id(item2_resp)

        # Toggle элемент в первом чеклисте
        toggle1_resp = await client.post(
            f"{API}/tasks/{task['task_id']}/checklists/{cl1_id}/items/{item1_id}/toggle",
            headers=headers,
        )
        assert toggle1_resp.status_code == 200

        # Toggle элемент во втором чеклисте
        toggle2_resp = await client.post(
            f"{API}/tasks/{task['task_id']}/checklists/{cl2_id}/items/{item2_id}/toggle",
            headers=headers,
        )
        assert toggle2_resp.status_code == 200

    async def test_delete_one_checklist_keeps_others(self, client: AsyncClient, project_owner):
        """200 — удаление одного чеклиста не затрагивает другой."""
        proj = project_owner
        task = await create_task(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        headers = auth_headers(proj["access_token"])

        # Создаём два чеклиста
        cl1_resp = await client.post(
            f"{API}/tasks/{task['task_id']}/checklists",
            json={"title": "To Delete"},
            headers=headers,
        )
        assert cl1_resp.status_code == 201
        cl1_id = _extract_id(cl1_resp)

        cl2_resp = await client.post(
            f"{API}/tasks/{task['task_id']}/checklists",
            json={"title": "To Keep"},
            headers=headers,
        )
        assert cl2_resp.status_code == 201
        cl2_id = _extract_id(cl2_resp)

        # Добавляем элемент во второй чеклист
        item_resp = await client.post(
            f"{API}/tasks/{task['task_id']}/checklists/{cl2_id}/items",
            json={"text": "Survivor"},
            headers=headers,
        )
        assert item_resp.status_code == 201

        # Удаляем первый чеклист
        del_resp = await client.delete(
            f"{API}/tasks/{task['task_id']}/checklists/{cl1_id}",
            headers=headers,
        )
        assert del_resp.status_code == 200

        # Задача всё ещё существует
        get_resp = await client.get(
            f"{API}/tasks/{task['task_id']}",
            headers=headers,
        )
        assert get_resp.status_code == 200

    async def test_assign_item_in_second_checklist(self, client: AsyncClient, project_owner):
        """200 — назначение исполнителя на элемент второго чеклиста."""
        proj = project_owner
        task = await create_task(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        headers = auth_headers(proj["access_token"])

        # Создаём два чеклиста
        cl1_resp = await client.post(
            f"{API}/tasks/{task['task_id']}/checklists",
            json={"title": "Checklist A"},
            headers=headers,
        )
        assert cl1_resp.status_code == 201
        cl1_id = _extract_id(cl1_resp)

        cl2_resp = await client.post(
            f"{API}/tasks/{task['task_id']}/checklists",
            json={"title": "Checklist B"},
            headers=headers,
        )
        assert cl2_resp.status_code == 201
        cl2_id = _extract_id(cl2_resp)

        # Элемент во втором чеклисте
        item_resp = await client.post(
            f"{API}/tasks/{task['task_id']}/checklists/{cl2_id}/items",
            json={"text": "Task for assignee"},
            headers=headers,
        )
        assert item_resp.status_code == 201
        item_id = _extract_id(item_resp)

        # Назначаем исполнителя
        assign_resp = await client.post(
            f"{API}/tasks/{task['task_id']}/checklists/{cl2_id}/items/{item_id}/assign",
            json={"assignee_id": proj["user_id"]},
            headers=headers,
        )
        assert assign_resp.status_code == 200

    async def test_three_checklists_with_items(self, client: AsyncClient, project_owner):
        """200 — три чеклиста с несколькими элементами в каждом."""
        proj = project_owner
        task = await create_task(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        headers = auth_headers(proj["access_token"])
        checklist_ids = []

        for i in range(3):
            cl_resp = await client.post(
                f"{API}/tasks/{task['task_id']}/checklists",
                json={"title": f"Checklist {i + 1}"},
                headers=headers,
            )
            assert cl_resp.status_code == 201
            checklist_ids.append(_extract_id(cl_resp))

        # Добавляем по 2 элемента в каждый чеклист
        for cl_id in checklist_ids:
            for j in range(2):
                item_resp = await client.post(
                    f"{API}/tasks/{task['task_id']}/checklists/{cl_id}/items",
                    json={"text": f"Item {j + 1}"},
                    headers=headers,
                )
                assert item_resp.status_code == 201

        # Toggle один элемент в каждом чеклисте
        for cl_id in checklist_ids:
            # Создаём ещё по одному элементу и toggle
            item_resp = await client.post(
                f"{API}/tasks/{task['task_id']}/checklists/{cl_id}/items",
                json={"text": "Toggle me"},
                headers=headers,
            )
            assert item_resp.status_code == 201
            item_id = _extract_id(item_resp)

            toggle_resp = await client.post(
                f"{API}/tasks/{task['task_id']}/checklists/{cl_id}/items/{item_id}/toggle",
                headers=headers,
            )
            assert toggle_resp.status_code == 200

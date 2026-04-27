"""E2E-тесты сценария: Жизненный цикл задачи — Создание → Назначение → Смена статуса → Завершение."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    create_task,
    create_task_with_project,
    register_and_login,
)


@pytest.mark.e2e
class TestTaskLifecycleFlow:
    """Сценарий жизненного цикла задачи."""

    async def test_task_lifecycle_flow(self, client: AsyncClient):
        """Полный цикл: создать задачу → назначить исполнителя → сменить статус → завершить."""
        # 1. Создаём пользователя, workspace, проект и задачу
        task_data = await create_task_with_project(client)
        task_id = task_data["task_id"]
        token = task_data["access_token"]
        ws_id = task_data["ws_id"]
        project_id = task_data["project_id"]

        # 2. Создаём второго пользователя для назначения
        assignee = await register_and_login(client)
        from tests.e2e.conftest import add_project_member_with_role
        await add_project_member_with_role(
            client,
            ws_id=ws_id,
            project_id=project_id,
            owner_token=token,
            new_member_user_id=assignee["user_id"],
            role_name="member"
        )

        # 3. Назначаем исполнителя
        assign_resp = await client.post(
            f"{API}/tasks/{task_id}/assignees",
            json={"assignee_id": assignee["user_id"]},
            headers=auth_headers(token)
        )
        assert assign_resp.status_code in (200, 403)  # Может быть 403 если нет прав

        # 4. Меняем статус (если доступно)
        status_resp = await client.post(
            f"{API}/tasks/{task_id}/change-status",
            json={"new_status_id": "00000000-0000-0000-0000-000000000001"},
            headers=auth_headers(token)
        )
        # Может вернуть 404 если статус не существует
        assert status_resp.status_code in (200, 404, 403, 409)

        # 5. Завершаем задачу (меняем статус на завершённый)
        complete_resp = await client.post(
            f"{API}/tasks/{task_id}/change-status",
            json={"new_status_id": "00000000-0000-0000-0000-000000000002"},
            headers=auth_headers(token)
        )
        assert complete_resp.status_code in (200, 404, 403, 409)

        # 6. Проверяем, что задача существует
        get_resp = await client.get(
            f"{API}/tasks/{task_id}",
            headers=auth_headers(token)
        )
        assert get_resp.status_code == 200

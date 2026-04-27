"""E2E-тесты: POST /tasks/{task_id}/assignees — Назначение исполнителя."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    create_task,
    register_and_login,
)


@pytest.mark.e2e
class TestAssignTask:
    """Назначение исполнителя."""

    async def test_assign_task_success(self, client: AsyncClient, project_owner):
        """200 — исполнитель назначен."""
        proj = project_owner
        task = await create_task(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        assignee = await register_and_login(client)
        # Сначала добавляем пользователя в проект
        from tests.e2e.conftest import add_project_member_with_role
        await add_project_member_with_role(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            owner_token=proj["access_token"],
            new_member_user_id=assignee["user_id"],
            role_name="member"
        )
        resp = await client.post(
            f"{API}/tasks/{task['task_id']}/assignees",
            json={"assignee_id": assignee["user_id"]},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 200

    async def test_assign_task_no_auth(self, client: AsyncClient, project_owner):
        """401 — без токена авторизации."""
        proj = project_owner
        task = await create_task(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        assignee = await register_and_login(client)
        resp = await client.post(
            f"{API}/tasks/{task['task_id']}/assignees",
            json={"assignee_id": assignee["user_id"]}
        )
        assert resp.status_code == 401

    async def test_assign_task_forbidden(self, client: AsyncClient, project_owner):
        """403 — пользователь не участник проекта."""
        proj = project_owner
        task = await create_task(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        assignee = await register_and_login(client)
        stranger = await register_and_login(client)
        resp = await client.post(
            f"{API}/tasks/{task['task_id']}/assignees",
            json={"assignee_id": assignee["user_id"]},
            headers=auth_headers(stranger["access_token"])
        )
        assert resp.status_code == 403

    async def test_assign_task_not_found(self, client: AsyncClient, project_owner):
        """404 — задача не найдена."""
        proj = project_owner
        assignee = await register_and_login(client)
        resp = await client.post(
            f"{API}/tasks/00000000-0000-0000-0000-000000000000/assignees",
            json={"assignee_id": assignee["user_id"]},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 404

    async def test_assign_task_validation_missing_assignee_id(self, client: AsyncClient, project_owner):
        """422 — отсутствует assignee_id."""
        proj = project_owner
        task = await create_task(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        resp = await client.post(
            f"{API}/tasks/{task['task_id']}/assignees",
            json={},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 422

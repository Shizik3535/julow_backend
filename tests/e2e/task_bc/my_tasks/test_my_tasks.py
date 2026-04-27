"""E2E-тесты: GET /tasks/mine — Мои задачи."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    create_task,
    register_and_login,
)


@pytest.mark.e2e
class TestMyTasks:
    """Мои задачи."""

    async def test_my_tasks_success(self, client: AsyncClient):
        """200 — список задач текущего пользователя."""
        user = await register_and_login(client)
        # Создаём workspace, project и task для пользователя
        from tests.e2e.conftest import create_workspace, create_project
        ws = await create_workspace(client, token=user["access_token"], name="My WS")
        proj = await create_project(client, ws_id=ws["ws_id"], token=user["access_token"])
        await create_task(
            client,
            ws_id=ws["ws_id"],
            project_id=proj["project_id"],
            token=user["access_token"],
            title="My Task"
        )
        resp = await client.get(
            f"{API}/tasks/mine",
            headers=auth_headers(user["access_token"])
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "total" in data

    async def test_my_tasks_empty(self, client: AsyncClient):
        """200 — пустой список задач."""
        user = await register_and_login(client)
        resp = await client.get(
            f"{API}/tasks/mine",
            headers=auth_headers(user["access_token"])
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0
        assert len(data["items"]) == 0

    async def test_my_tasks_no_auth(self, client: AsyncClient):
        """401 — без токена авторизации."""
        resp = await client.get(f"{API}/tasks/mine")
        assert resp.status_code == 401

    async def test_my_tasks_with_pagination(self, client: AsyncClient):
        """200 — пагинация работает."""
        user = await register_and_login(client)
        from tests.e2e.conftest import create_workspace, create_project
        ws = await create_workspace(client, token=user["access_token"], name="My WS")
        proj = await create_project(client, ws_id=ws["ws_id"], token=user["access_token"])
        for i in range(5):
            await create_task(
                client,
                ws_id=ws["ws_id"],
                project_id=proj["project_id"],
                token=user["access_token"],
                title=f"Task {i}"
            )
        resp = await client.get(
            f"{API}/tasks/mine",
            params={"offset": 0, "limit": 2},
            headers=auth_headers(user["access_token"])
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 2

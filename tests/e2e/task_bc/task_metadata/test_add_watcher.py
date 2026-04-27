"""E2E-тесты: POST /tasks/{task_id}/watchers — Добавление наблюдателя к задаче."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    create_task,
    register_and_login,
)


@pytest.mark.e2e
class TestAddWatcher:
    """Добавление наблюдателя к задаче."""

    async def test_add_watcher_success(self, client: AsyncClient, project_owner):
        """200 — наблюдатель добавлен."""
        proj = project_owner
        task = await create_task(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        watcher = await register_and_login(client)
        from tests.e2e.conftest import add_project_member_with_role
        await add_project_member_with_role(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            owner_token=proj["access_token"],
            new_member_user_id=watcher["user_id"],
            role_name="member"
        )
        resp = await client.post(
            f"{API}/tasks/{task['task_id']}/watchers",
            json={"user_id": watcher["user_id"]},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 200

    async def test_add_watcher_no_auth(self, client: AsyncClient, project_owner):
        """401 — без токена авторизации."""
        proj = project_owner
        task = await create_task(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        watcher = await register_and_login(client)
        resp = await client.post(
            f"{API}/tasks/{task['task_id']}/watchers",
            json={"user_id": watcher["user_id"]}
        )
        assert resp.status_code == 401

    async def test_add_watcher_forbidden(self, client: AsyncClient, project_owner):
        """403 — пользователь не участник проекта."""
        proj = project_owner
        task = await create_task(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        watcher = await register_and_login(client)
        stranger = await register_and_login(client)
        resp = await client.post(
            f"{API}/tasks/{task['task_id']}/watchers",
            json={"user_id": watcher["user_id"]},
            headers=auth_headers(stranger["access_token"])
        )
        assert resp.status_code == 403

    async def test_add_watcher_not_found(self, client: AsyncClient, project_owner):
        """404 — задача не найдена."""
        proj = project_owner
        watcher = await register_and_login(client)
        resp = await client.post(
            f"{API}/tasks/00000000-0000-0000-0000-000000000000/watchers",
            json={"user_id": watcher["user_id"]},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 404

    async def test_add_watcher_validation_missing_user_id(self, client: AsyncClient, project_owner):
        """422 — отсутствует user_id."""
        proj = project_owner
        task = await create_task(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            token=proj["access_token"]
        )
        resp = await client.post(
            f"{API}/tasks/{task['task_id']}/watchers",
            json={},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 422

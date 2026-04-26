"""E2E-тесты: GET /workspaces/{ws_id}/projects/{project_id}/epics — Эпики проекта (чтение)."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    register_and_login,
    add_project_member_with_role
)


@pytest.mark.e2e
class TestListEpics:
    """Список эпиков проекта (epics.read)."""

    async def test_list_epics_success_owner(self, client: AsyncClient, project_owner):
        """200 — owner получает список эпиков."""
        proj = project_owner
        resp = await client.get(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/epics",
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert isinstance(data, list)

    async def test_list_epics_success_manager(self, client: AsyncClient, project_owner):
        """200 — manager получает список эпиков (epics.*)."""
        proj = project_owner
        manager = await register_and_login(client)
        await add_project_member_with_role(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            owner_token=proj["access_token"],
            new_member_user_id=manager["user_id"],
            role_name="manager"
        )
        resp = await client.get(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/epics",
            headers=auth_headers(manager["access_token"])
        )
        assert resp.status_code == 200

    async def test_list_epics_no_auth(self, client: AsyncClient, project_owner):
        """401 — без токена."""
        proj = project_owner
        resp = await client.get(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/epics"
        )
        assert resp.status_code == 401


@pytest.mark.e2e
class TestGetEpic:
    """Получение эпика по ID (epics.read)."""

    async def test_get_epic_success(self, client: AsyncClient, project_owner):
        """200 — owner получает эпик."""
        proj = project_owner
        # Create epic first
        create_resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/epics",
            json={"name": "Auth Module"},
            headers=auth_headers(proj["access_token"])
        )
        assert create_resp.status_code == 201
        epic_id = create_resp.json()["data"]["id"]
        resp = await client.get(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/epics/{epic_id}",
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["id"] == epic_id

    async def test_get_epic_no_auth(self, client: AsyncClient, project_owner):
        """401 — без токена."""
        proj = project_owner
        resp = await client.get(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/epics/00000000-0000-0000-0000-000000000000"
        )
        assert resp.status_code == 401

"""E2E-тесты: GET /workspaces/{ws_id}/projects/{project_id}/sprints — Спринты проекта (чтение)."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    register_and_login,
    add_project_member_with_role
)


@pytest.mark.e2e
class TestListSprints:
    """Список спринтов проекта (sprints.read)."""

    async def test_list_sprints_success_owner(self, client: AsyncClient, project_owner):
        """200 — owner получает список спринтов."""
        proj = project_owner
        resp = await client.get(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/sprints",
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert isinstance(data, list)

    async def test_list_sprints_success_member(self, client: AsyncClient, project_owner):
        """200 — member получает список спринтов (sprints.read)."""
        proj = project_owner
        member = await register_and_login(client)
        await add_project_member_with_role(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            owner_token=proj["access_token"],
            new_member_user_id=member["user_id"],
            role_name="member"
        )
        resp = await client.get(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/sprints",
            headers=auth_headers(member["access_token"])
        )
        assert resp.status_code == 200

    async def test_list_sprints_no_auth(self, client: AsyncClient, project_owner):
        """401 — без токена."""
        proj = project_owner
        resp = await client.get(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/sprints"
        )
        assert resp.status_code == 401


@pytest.mark.e2e
class TestGetSprint:
    """Получение спринта по ID и активного спринта (sprints.read)."""

    async def test_get_sprint_success(self, client: AsyncClient, project_owner):
        """200 — owner получает спринт по ID."""
        proj = project_owner
        # Create sprint first
        create_resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/sprints",
            json={"name": "Sprint 1"},
            headers=auth_headers(proj["access_token"])
        )
        assert create_resp.status_code == 201
        sprint_id = create_resp.json()["data"]["id"]
        resp = await client.get(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/sprints/{sprint_id}",
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["id"] == sprint_id

    async def test_get_active_sprint_not_found(self, client: AsyncClient, project_owner):
        """404 — нет активного спринта."""
        proj = project_owner
        resp = await client.get(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/sprints/active",
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 404

    async def test_get_sprint_no_auth(self, client: AsyncClient, project_owner):
        """401 — без токена."""
        proj = project_owner
        resp = await client.get(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/sprints/00000000-0000-0000-0000-000000000000"
        )
        assert resp.status_code == 401

"""E2E-тесты: GET /workspaces/{ws_id}/projects/{project_id} — Получение проекта."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    register_and_login,
    add_project_member_with_role
)


@pytest.mark.e2e
class TestGetProject:
    """Получение проекта (project.read)."""

    async def test_get_success_owner(self, client: AsyncClient, project_owner):
        """200 — owner получает проект."""
        proj = project_owner
        resp = await client.get(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}",
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["id"] == proj["project_id"]
        assert data["name"] == proj["project_name"]

    async def test_get_success_member(self, client: AsyncClient, project_owner):
        """200 — member с project.read может получить проект."""
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
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}",
            headers=auth_headers(member["access_token"])
        )
        assert resp.status_code == 200

    async def test_get_no_auth(self, client: AsyncClient, project_owner):
        """401 — без токена."""
        proj = project_owner
        resp = await client.get(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}"
        )
        assert resp.status_code == 401

    async def test_get_forbidden_non_member(self, client: AsyncClient, project_owner):
        """403 — пользователь не участник проекта."""
        proj = project_owner
        stranger = await register_and_login(client)
        resp = await client.get(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}",
            headers=auth_headers(stranger["access_token"])
        )
        assert resp.status_code == 403

    async def test_get_not_found(self, client: AsyncClient):
        """404 — несуществующий проект."""
        user = await register_and_login(client)
        ws_resp = await client.post(
            f"{API}/workspaces/",
            json={"name": "WS for 404"},
            headers=auth_headers(user["access_token"])
        )
        ws_id = ws_resp.json()["data"]["id"]
        resp = await client.get(
            f"{API}/workspaces/{ws_id}/projects/00000000-0000-0000-0000-000000000000",
            headers=auth_headers(user["access_token"])
        )
        assert resp.status_code == 404

"""E2E-тесты: GET /workspaces/{ws_id}/projects/{project_id}/board — Доска проекта."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    register_and_login,
    add_project_member_with_role
)


@pytest.mark.e2e
class TestGetBoard:
    """Получение доски проекта (project.read)."""

    async def test_get_board_success_member(self, client: AsyncClient, project_owner):
        """200 — member получает доску проекта (project.read)."""
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
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/board",
            headers=auth_headers(member["access_token"])
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["id"]

    async def test_get_board_success_owner(self, client: AsyncClient, project_owner):
        """200 — owner получает доску проекта."""
        proj = project_owner
        resp = await client.get(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/board",
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 200

    async def test_get_board_no_auth(self, client: AsyncClient, project_owner):
        """401 — без токена."""
        proj = project_owner
        resp = await client.get(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/board"
        )
        assert resp.status_code == 401

    async def test_get_board_forbidden_non_member(self, client: AsyncClient, project_owner):
        """403 — пользователь не участник проекта."""
        proj = project_owner
        stranger = await register_and_login(client)
        resp = await client.get(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/board",
            headers=auth_headers(stranger["access_token"])
        )
        assert resp.status_code == 403

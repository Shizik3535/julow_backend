"""E2E-тесты: GET /workspaces/{ws_id}/projects/{project_id}/members — Участники проекта."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    register_and_login,
    add_project_member_with_role
)


@pytest.mark.e2e
class TestListProjectMembers:
    """Список участников проекта (members.read)."""

    async def test_list_members_success_owner(self, client: AsyncClient, project_owner):
        """200 — owner получает список участников."""
        proj = project_owner
        resp = await client.get(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/members",
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert isinstance(data, list)
        assert len(data) >= 1

    async def test_list_members_success_manager(self, client: AsyncClient, project_owner):
        """200 — manager получает список (members.read)."""
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
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/members",
            headers=auth_headers(manager["access_token"])
        )
        assert resp.status_code == 200

    async def test_list_members_no_auth(self, client: AsyncClient, project_owner):
        """401 — без токена."""
        proj = project_owner
        resp = await client.get(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/members"
        )
        assert resp.status_code == 401

    async def test_list_members_forbidden_guest(self, client: AsyncClient, project_owner):
        """403 — guest (нет members.read)."""
        proj = project_owner
        guest = await register_and_login(client)
        await add_project_member_with_role(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            owner_token=proj["access_token"],
            new_member_user_id=guest["user_id"],
            role_name="guest"
        )
        resp = await client.get(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/members",
            headers=auth_headers(guest["access_token"])
        )
        assert resp.status_code == 403


@pytest.mark.e2e
class TestGetProjectMember:
    """Получение конкретного участника проекта (members.read)."""

    async def test_get_member_success(self, client: AsyncClient, project_owner):
        """200 — admin получает участника."""
        proj = project_owner
        admin = await register_and_login(client)
        await add_project_member_with_role(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            owner_token=proj["access_token"],
            new_member_user_id=admin["user_id"],
            role_name="admin"
        )
        resp = await client.get(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/members/{admin['user_id']}",
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 200

    async def test_get_member_no_auth(self, client: AsyncClient, project_owner):
        """401 — без токена."""
        proj = project_owner
        resp = await client.get(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/members/{proj['user_id']}"
        )
        assert resp.status_code == 401

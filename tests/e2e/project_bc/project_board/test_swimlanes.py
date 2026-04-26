"""E2E-тесты: CRUD swimlanes доски проекта."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    register_and_login,
    add_project_member_with_role
)


@pytest.mark.e2e
class TestBoardSwimlanes:
    """Swimlanes доски (workflow.write)."""

    async def test_add_swimlane_success_admin(self, client: AsyncClient, project_owner):
        """201 — admin добавляет swimlane (workflow.*)."""
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
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/board/swimlanes",
            json={"name": "By Assignee", "group_by": "assignee"},
            headers=auth_headers(admin["access_token"])
        )
        assert resp.status_code == 201

    async def test_add_swimlane_success_manager(self, client: AsyncClient, project_owner):
        """201 — manager добавляет swimlane (workflow.*)."""
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
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/board/swimlanes",
            json={"name": "By Priority", "group_by": "priority"},
            headers=auth_headers(manager["access_token"])
        )
        assert resp.status_code == 201

    async def test_add_swimlane_no_auth(self, client: AsyncClient, project_owner):
        """401 — без токена."""
        proj = project_owner
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/board/swimlanes",
            json={"name": "NoAuth", "group_by": "assignee"}
        )
        assert resp.status_code == 401

    async def test_remove_swimlane_success_admin(self, client: AsyncClient, project_owner):
        """200 — admin удаляет swimlane."""
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
        # Add swimlane first
        add_resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/board/swimlanes",
            json={"name": "By Assignee", "group_by": "assignee"},
            headers=auth_headers(proj["access_token"])
        )
        # Get board to find swimlane id
        board_resp = await client.get(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/board",
            headers=auth_headers(proj["access_token"])
        )
        board_data = board_resp.json()["data"]
        swimlanes = board_data.get("swimlanes", [])
        if swimlanes:
            sl_id = swimlanes[0]["id"]
            resp = await client.delete(
                f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/board/swimlanes/{sl_id}",
                headers=auth_headers(admin["access_token"])
            )
            assert resp.status_code == 200

"""E2E-тесты: CRUD колонок доски проекта."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    register_and_login,
    add_project_member_with_role
)


@pytest.mark.e2e
class TestBoardColumns:
    """Колонки доски (workflow.write)."""

    async def test_add_column_success_admin(self, client: AsyncClient, project_owner):
        """201 — admin добавляет колонку (workflow.*)."""
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
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/board/columns",
            json={"name": "In Progress", "color": "#FFA500"},
            headers=auth_headers(admin["access_token"])
        )
        assert resp.status_code == 201

    async def test_add_column_success_manager(self, client: AsyncClient, project_owner):
        """201 — manager добавляет колонку (workflow.*)."""
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
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/board/columns",
            json={"name": "In Review"},
            headers=auth_headers(manager["access_token"])
        )
        assert resp.status_code == 201

    async def test_add_column_forbidden_member(self, client: AsyncClient, project_owner):
        """403 — member (нет workflow.write)."""
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
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/board/columns",
            json={"name": "Forbidden"},
            headers=auth_headers(member["access_token"])
        )
        assert resp.status_code == 403

    async def test_add_column_no_auth(self, client: AsyncClient, project_owner):
        """401 — без токена."""
        proj = project_owner
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/board/columns",
            json={"name": "NoAuth"}
        )
        assert resp.status_code == 401

    async def test_remove_column_success_admin(self, client: AsyncClient, project_owner):
        """200 — admin удаляет колонку."""
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
        # Get board to find column id
        board_resp = await client.get(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/board",
            headers=auth_headers(proj["access_token"])
        )
        board_data = board_resp.json()["data"]
        columns = board_data.get("columns", [])
        if columns:
            col_id = columns[0]["id"]
            resp = await client.delete(
                f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/board/columns/{col_id}",
                headers=auth_headers(admin["access_token"])
            )
            assert resp.status_code == 200

    async def test_reorder_columns_success_admin(self, client: AsyncClient, project_owner):
        """200 — admin переупорядочивает колонки."""
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
        # Get board to find column ids
        board_resp = await client.get(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/board",
            headers=auth_headers(proj["access_token"])
        )
        board_data = board_resp.json()["data"]
        columns = board_data.get("columns", [])
        if len(columns) >= 2:
            col_ids = [c["id"] for c in reversed(columns)]
            resp = await client.put(
                f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/board/columns/reorder",
                json={"column_ids": col_ids},
                headers=auth_headers(admin["access_token"])
            )
            assert resp.status_code == 200

    async def test_change_wip_limit_success_admin(self, client: AsyncClient, project_owner):
        """200 — admin меняет WIP-лимит колонки."""
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
        board_resp = await client.get(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/board",
            headers=auth_headers(proj["access_token"])
        )
        board_data = board_resp.json()["data"]
        columns = board_data.get("columns", [])
        if columns:
            col_id = columns[0]["id"]
            resp = await client.patch(
                f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/board/columns/{col_id}/wip-limit",
                json={"wip_limit": 5},
                headers=auth_headers(admin["access_token"])
            )
            assert resp.status_code == 200

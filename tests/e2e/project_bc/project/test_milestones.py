"""E2E-тесты: CRUD milestones проекта."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    register_and_login,
    add_project_member_with_role
)


@pytest.mark.e2e
class TestMilestones:
    """Milestones проекта (milestones.write)."""

    async def test_add_milestone_success_manager(self, client: AsyncClient, project_owner):
        """201 — manager добавляет milestone (milestones.*)."""
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
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/milestones",
            json={"name": "v1.0 Release", "due_date": "2026-12-31"},
            headers=auth_headers(manager["access_token"])
        )
        assert resp.status_code == 201
        data = resp.json()["data"]
        assert data["id"]
        assert data["name"] == "v1.0 Release"

    async def test_add_milestone_success_owner(self, client: AsyncClient, project_owner):
        """201 — owner добавляет milestone (project.*)."""
        proj = project_owner
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/milestones",
            json={"name": "v1.0 Release", "due_date": "2026-12-31"},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 201

    async def test_update_milestone_success(self, client: AsyncClient, project_owner):
        """200 — manager обновляет milestone."""
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
        ms_resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/milestones",
            json={"name": "v1.0", "due_date": "2026-12-31"},
            headers=auth_headers(proj["access_token"])
        )
        ms_id = ms_resp.json()["data"]["id"]
        resp = await client.patch(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/milestones/{ms_id}",
            json={"name": "v2.0"},
            headers=auth_headers(manager["access_token"])
        )
        assert resp.status_code == 200

    async def test_change_milestone_status_success(self, client: AsyncClient, project_owner):
        """200 — manager меняет статус milestone."""
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
        ms_resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/milestones",
            json={"name": "v1.0", "due_date": "2026-12-31"},
            headers=auth_headers(proj["access_token"])
        )
        ms_id = ms_resp.json()["data"]["id"]
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/milestones/{ms_id}/change-status",
            json={"new_status": "in_progress"},
            headers=auth_headers(manager["access_token"])
        )
        assert resp.status_code == 200

    async def test_add_milestone_forbidden_member(self, client: AsyncClient, project_owner):
        """403 — member (нет milestones.write)."""
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
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/milestones",
            json={"name": "v1.0", "due_date": "2026-12-31"},
            headers=auth_headers(member["access_token"])
        )
        assert resp.status_code == 403

    async def test_add_milestone_no_auth(self, client: AsyncClient, project_owner):
        """401 — без токена."""
        proj = project_owner
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/milestones",
            json={"name": "v1.0", "due_date": "2026-12-31"}
        )
        assert resp.status_code == 401

    async def test_add_milestone_validation_empty_name(self, client: AsyncClient, project_owner):
        """422 — пустое название milestone."""
        proj = project_owner
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/milestones",
            json={"name": "", "due_date": "2026-12-31"},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 422

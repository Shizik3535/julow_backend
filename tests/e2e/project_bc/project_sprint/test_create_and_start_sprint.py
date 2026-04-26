"""E2E-тесты: POST /workspaces/{ws_id}/projects/{project_id}/sprints — Создание и запуск спринта."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    register_and_login,
    add_project_member_with_role
)


@pytest.mark.e2e
class TestCreateSprint:
    """Создание спринта (sprints.write)."""

    async def test_create_sprint_success_manager(self, client: AsyncClient, project_owner):
        """201 — manager создаёт спринт (sprints.*)."""
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
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/sprints",
            json={"name": "Sprint 1", "goal": "Complete auth module"},
            headers=auth_headers(manager["access_token"])
        )
        assert resp.status_code == 201
        data = resp.json()["data"]
        assert data["id"]
        assert data["name"] == "Sprint 1"

    async def test_create_sprint_success_owner(self, client: AsyncClient, project_owner):
        """201 — owner создаёт спринт (project.*)."""
        proj = project_owner
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/sprints",
            json={"name": "Sprint 1"},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 201

    async def test_create_sprint_forbidden_member(self, client: AsyncClient, project_owner):
        """403 — member (только sprints.read)."""
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
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/sprints",
            json={"name": "Forbidden Sprint"},
            headers=auth_headers(member["access_token"])
        )
        assert resp.status_code == 403

    async def test_create_sprint_no_auth(self, client: AsyncClient, project_owner):
        """401 — без токена."""
        proj = project_owner
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/sprints",
            json={"name": "NoAuth Sprint"}
        )
        assert resp.status_code == 401

    async def test_create_sprint_validation_empty_name(self, client: AsyncClient, project_owner):
        """422 — пустое название спринта."""
        proj = project_owner
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/sprints",
            json={"name": ""},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 422


@pytest.mark.e2e
class TestStartSprint:
    """Запуск спринта (sprints.write)."""

    async def test_start_sprint_success_manager(self, client: AsyncClient, project_owner):
        """200 — manager запускает спринт."""
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
        create_resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/sprints",
            json={"name": "Sprint 1"},
            headers=auth_headers(proj["access_token"])
        )
        sprint_id = create_resp.json()["data"]["id"]
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/sprints/{sprint_id}/start",
            headers=auth_headers(manager["access_token"])
        )
        assert resp.status_code == 200

    async def test_start_sprint_forbidden_member(self, client: AsyncClient, project_owner):
        """403 — member (только sprints.read)."""
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
        create_resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/sprints",
            json={"name": "Sprint 1"},
            headers=auth_headers(proj["access_token"])
        )
        sprint_id = create_resp.json()["data"]["id"]
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/sprints/{sprint_id}/start",
            headers=auth_headers(member["access_token"])
        )
        assert resp.status_code == 403

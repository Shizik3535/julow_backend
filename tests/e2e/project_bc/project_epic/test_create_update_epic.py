"""E2E-тесты: POST/PATCH/POST change-status эпиков проекта."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    register_and_login,
    add_project_member_with_role
)


@pytest.mark.e2e
class TestCreateEpic:
    """Создание эпика (epics.write)."""

    async def test_create_epic_success_manager(self, client: AsyncClient, project_owner):
        """201 — manager создаёт эпик (epics.*)."""
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
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/epics",
            json={"name": "Auth Module"},
            headers=auth_headers(manager["access_token"])
        )
        assert resp.status_code == 201
        data = resp.json()["data"]
        assert data["id"]
        assert data["name"] == "Auth Module"

    async def test_create_epic_success_owner(self, client: AsyncClient, project_owner):
        """201 — owner создаёт эпик (project.*)."""
        proj = project_owner
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/epics",
            json={"name": "Auth Module"},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 201

    async def test_create_epic_forbidden_member(self, client: AsyncClient, project_owner):
        """403 — member (нет epics.write)."""
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
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/epics",
            json={"name": "Forbidden Epic"},
            headers=auth_headers(member["access_token"])
        )
        assert resp.status_code == 403

    async def test_create_epic_no_auth(self, client: AsyncClient, project_owner):
        """401 — без токена."""
        proj = project_owner
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/epics",
            json={"name": "NoAuth Epic"}
        )
        assert resp.status_code == 401

    async def test_create_epic_validation_empty_name(self, client: AsyncClient, project_owner):
        """422 — пустое название эпика."""
        proj = project_owner
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/epics",
            json={"name": ""},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 422


@pytest.mark.e2e
class TestUpdateEpic:
    """Обновление эпика (epics.write)."""

    async def test_update_epic_success_manager(self, client: AsyncClient, project_owner):
        """200 — manager обновляет эпик."""
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
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/epics",
            json={"name": "Auth Module"},
            headers=auth_headers(proj["access_token"])
        )
        epic_id = create_resp.json()["data"]["id"]
        resp = await client.patch(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/epics/{epic_id}",
            json={"name": "Auth V2"},
            headers=auth_headers(manager["access_token"])
        )
        assert resp.status_code == 200

    async def test_update_epic_forbidden_member(self, client: AsyncClient, project_owner):
        """403 — member (нет epics.write)."""
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
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/epics",
            json={"name": "Auth Module"},
            headers=auth_headers(proj["access_token"])
        )
        epic_id = create_resp.json()["data"]["id"]
        resp = await client.patch(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/epics/{epic_id}",
            json={"name": "Forbidden"},
            headers=auth_headers(member["access_token"])
        )
        assert resp.status_code == 403


@pytest.mark.e2e
class TestChangeEpicStatus:
    """Изменение статуса эпика (epics.write)."""

    async def test_change_status_success_manager(self, client: AsyncClient, project_owner):
        """200 — manager меняет статус эпика."""
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
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/epics",
            json={"name": "Auth Module"},
            headers=auth_headers(proj["access_token"])
        )
        epic_id = create_resp.json()["data"]["id"]
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/epics/{epic_id}/change-status",
            json={"new_status": "in_progress"},
            headers=auth_headers(manager["access_token"])
        )
        assert resp.status_code == 200

    async def test_change_status_forbidden_member(self, client: AsyncClient, project_owner):
        """403 — member (нет epics.write)."""
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
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/epics",
            json={"name": "Auth Module"},
            headers=auth_headers(proj["access_token"])
        )
        epic_id = create_resp.json()["data"]["id"]
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/epics/{epic_id}/change-status",
            json={"new_status": "in_progress"},
            headers=auth_headers(member["access_token"])
        )
        assert resp.status_code == 403

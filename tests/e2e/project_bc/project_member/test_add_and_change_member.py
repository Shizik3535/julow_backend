"""E2E-тесты: POST /workspaces/{ws_id}/projects/{project_id}/members — Добавление участника."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    register_and_login,
    register_user,
    add_project_member_with_role,
    add_ws_member_with_role
)


@pytest.mark.e2e
class TestAddProjectMember:
    """Добавление участника в проект (members.write)."""

    async def test_add_member_success_admin(self, client: AsyncClient, project_owner):
        """201 — admin добавляет участника (members.*)."""
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
        new_user = await register_user(client)
        await add_ws_member_with_role(
            client,
            ws_id=proj["ws_id"],
            owner_token=proj["access_token"],
            new_member_user_id=new_user["user_id"],
            role_name="member"
        )
        roles_resp = await client.get(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/roles",
            headers=auth_headers(proj["access_token"])
        )
        roles_data = roles_resp.json().get("data", [])
        roles = roles_data if isinstance(roles_data, list) else roles_data.get("items", [])
        member_role_id = ""
        for r in roles:
            if r.get("name") == "member":
                member_role_id = r.get("id", "")
                break
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/members",
            json={"user_id": new_user["user_id"], "role_id": member_role_id},
            headers=auth_headers(admin["access_token"])
        )
        assert resp.status_code == 201

    async def test_add_member_success_owner(self, client: AsyncClient, project_owner):
        """201 — owner добавляет участника (project.*)."""
        proj = project_owner
        new_user = await register_user(client)
        await add_ws_member_with_role(
            client,
            ws_id=proj["ws_id"],
            owner_token=proj["access_token"],
            new_member_user_id=new_user["user_id"],
            role_name="member"
        )
        roles_resp = await client.get(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/roles",
            headers=auth_headers(proj["access_token"])
        )
        roles_data = roles_resp.json().get("data", [])
        roles = roles_data if isinstance(roles_data, list) else roles_data.get("items", [])
        member_role_id = ""
        for r in roles:
            if r.get("name") == "member":
                member_role_id = r.get("id", "")
                break
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/members",
            json={"user_id": new_user["user_id"], "role_id": member_role_id},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 201

    async def test_add_member_no_auth(self, client: AsyncClient, project_owner):
        """401 — без токена."""
        proj = project_owner
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/members",
            json={"user_id": "some-user", "role_id": "some-role"}
        )
        assert resp.status_code == 401

    async def test_add_member_forbidden_manager(self, client: AsyncClient, project_owner):
        """403 — manager (только members.read)."""
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
        new_user = await register_user(client)
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/members",
            json={"user_id": new_user["user_id"], "role_id": "some-role"},
            headers=auth_headers(manager["access_token"])
        )
        assert resp.status_code == 403

    async def test_add_member_forbidden_member(self, client: AsyncClient, project_owner):
        """403 — member (нет members.write)."""
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
        new_user = await register_user(client)
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/members",
            json={"user_id": new_user["user_id"], "role_id": "some-role"},
            headers=auth_headers(member["access_token"])
        )
        assert resp.status_code == 403


@pytest.mark.e2e
class TestChangeProjectMemberRole:
    """Изменение роли участника проекта (members.write)."""

    async def test_change_role_success_admin(self, client: AsyncClient, project_owner):
        """200 — admin меняет роль участника."""
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
        member = await register_and_login(client)
        add_result = await add_project_member_with_role(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            owner_token=proj["access_token"],
            new_member_user_id=member["user_id"],
            role_name="member"
        )
        # Find manager role id
        roles_resp = await client.get(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/roles",
            headers=auth_headers(proj["access_token"])
        )
        roles_data = roles_resp.json().get("data", [])
        roles = roles_data if isinstance(roles_data, list) else roles_data.get("items", [])
        manager_role_id = ""
        for r in roles:
            if r.get("name") == "manager":
                manager_role_id = r.get("id", "")
                break
        resp = await client.patch(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/members/{member['user_id']}/role",
            json={"new_role_id": manager_role_id},
            headers=auth_headers(admin["access_token"])
        )
        assert resp.status_code == 200

    async def test_change_role_forbidden_manager(self, client: AsyncClient, project_owner):
        """403 — manager (только members.read)."""
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
        resp = await client.patch(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/members/{manager['user_id']}/role",
            json={"new_role_id": "some-role"},
            headers=auth_headers(manager["access_token"])
        )
        assert resp.status_code == 403

    async def test_change_role_no_auth(self, client: AsyncClient, project_owner):
        """401 — без токена."""
        proj = project_owner
        resp = await client.patch(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/members/{proj['user_id']}/role",
            json={"new_role_id": "some-role"}
        )
        assert resp.status_code == 401

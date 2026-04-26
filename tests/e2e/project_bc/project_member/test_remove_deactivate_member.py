"""E2E-тесты: DELETE/POST members — Удаление, деактивация, реактивация участников проекта."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    register_and_login,
    add_project_member_with_role
)


@pytest.mark.e2e
class TestRemoveProjectMember:
    """Удаление участника проекта (members.write)."""

    async def test_remove_member_success_admin(self, client: AsyncClient, project_owner):
        """200 — admin удаляет участника."""
        proj = project_owner
        admin = await register_and_login(client)
        member = await register_and_login(client)
        await add_project_member_with_role(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            owner_token=proj["access_token"],
            new_member_user_id=admin["user_id"],
            role_name="admin"
        )
        await add_project_member_with_role(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            owner_token=proj["access_token"],
            new_member_user_id=member["user_id"],
            role_name="member"
        )
        resp = await client.delete(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/members/{member['user_id']}",
            headers=auth_headers(admin["access_token"])
        )
        assert resp.status_code == 200

    async def test_remove_member_forbidden_manager(self, client: AsyncClient, project_owner):
        """403 — manager (только members.read)."""
        proj = project_owner
        manager = await register_and_login(client)
        member = await register_and_login(client)
        await add_project_member_with_role(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            owner_token=proj["access_token"],
            new_member_user_id=manager["user_id"],
            role_name="manager"
        )
        await add_project_member_with_role(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            owner_token=proj["access_token"],
            new_member_user_id=member["user_id"],
            role_name="member"
        )
        resp = await client.delete(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/members/{member['user_id']}",
            headers=auth_headers(manager["access_token"])
        )
        assert resp.status_code == 403

    async def test_remove_member_no_auth(self, client: AsyncClient, project_owner):
        """401 — без токена."""
        proj = project_owner
        resp = await client.delete(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/members/{proj['user_id']}"
        )
        assert resp.status_code == 401


@pytest.mark.e2e
class TestDeactivateProjectMember:
    """Деактивация участника проекта (members.write)."""

    async def test_deactivate_success_admin(self, client: AsyncClient, project_owner):
        """200 — admin деактивирует участника."""
        proj = project_owner
        admin = await register_and_login(client)
        member = await register_and_login(client)
        await add_project_member_with_role(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            owner_token=proj["access_token"],
            new_member_user_id=admin["user_id"],
            role_name="admin"
        )
        await add_project_member_with_role(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            owner_token=proj["access_token"],
            new_member_user_id=member["user_id"],
            role_name="member"
        )
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/members/{member['user_id']}/deactivate",
            headers=auth_headers(admin["access_token"])
        )
        assert resp.status_code == 200

    async def test_deactivate_forbidden_manager(self, client: AsyncClient, project_owner):
        """403 — manager (только members.read)."""
        proj = project_owner
        manager = await register_and_login(client)
        member = await register_and_login(client)
        await add_project_member_with_role(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            owner_token=proj["access_token"],
            new_member_user_id=manager["user_id"],
            role_name="manager"
        )
        await add_project_member_with_role(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            owner_token=proj["access_token"],
            new_member_user_id=member["user_id"],
            role_name="member"
        )
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/members/{member['user_id']}/deactivate",
            headers=auth_headers(manager["access_token"])
        )
        assert resp.status_code == 403

    async def test_deactivate_no_auth(self, client: AsyncClient, project_owner):
        """401 — без токена."""
        proj = project_owner
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/members/{proj['user_id']}/deactivate"
        )
        assert resp.status_code == 401


@pytest.mark.e2e
class TestReactivateProjectMember:
    """Реактивация участника проекта (members.write)."""
    async def test_reactivate_forbidden_manager(self, client: AsyncClient, project_owner):
        """403 — manager (только members.read)."""
        proj = project_owner
        manager = await register_and_login(client)
        member = await register_and_login(client)
        await add_project_member_with_role(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            owner_token=proj["access_token"],
            new_member_user_id=manager["user_id"],
            role_name="manager"
        )
        await add_project_member_with_role(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            owner_token=proj["access_token"],
            new_member_user_id=member["user_id"],
            role_name="member"
        )
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/members/{member['user_id']}/reactivate",
            headers=auth_headers(manager["access_token"])
        )
        assert resp.status_code == 403
    async def test_reactivate_no_auth(self, client: AsyncClient, project_owner):
        """401 — без токена."""
        proj = project_owner
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/members/{proj['user_id']}/reactivate"
        )
        assert resp.status_code == 401
    async def test_reactivate_success_admin(self, client: AsyncClient, project_owner):
        """200 — admin реактивирует участника."""
        proj = project_owner
        admin = await register_and_login(client)
        member = await register_and_login(client)
        await add_project_member_with_role(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            owner_token=proj["access_token"],
            new_member_user_id=admin["user_id"],
            role_name="admin"
        )
        await add_project_member_with_role(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            owner_token=proj["access_token"],
            new_member_user_id=member["user_id"],
            role_name="member"
        )
        await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/members/{member['user_id']}/deactivate",
            headers=auth_headers(admin["access_token"])
        )
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/members/{member['user_id']}/reactivate",
            headers=auth_headers(admin["access_token"])
        )
        assert resp.status_code == 200

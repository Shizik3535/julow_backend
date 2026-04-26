"""E2E-тесты: PATCH /workspaces/{ws_id}/projects/{project_id} — Обновление информации проекта."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    register_and_login,
    add_project_member_with_role
)


@pytest.mark.e2e
class TestUpdateProjectInfo:
    """Обновление информации проекта (project.settings.write)."""

    async def test_update_success_owner(self, client: AsyncClient, project_owner):
        """200 — owner обновляет информацию."""
        proj = project_owner
        resp = await client.patch(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}",
            json={"name": "Updated Name"},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 200

    async def test_update_success_admin(self, client: AsyncClient, project_owner):
        """200 — admin обновляет информацию (project.settings.*)."""
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
        resp = await client.patch(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}",
            json={"name": "Admin Updated"},
            headers=auth_headers(admin["access_token"])
        )
        assert resp.status_code == 200

    async def test_update_no_auth(self, client: AsyncClient, project_owner):
        """401 — без токена."""
        proj = project_owner
        resp = await client.patch(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}",
            json={"name": "NoAuth"}
        )
        assert resp.status_code == 401

    async def test_update_forbidden_manager(self, client: AsyncClient, project_owner):
        """403 — manager (нет project.settings.write)."""
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
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}",
            json={"name": "Manager Updated"},
            headers=auth_headers(manager["access_token"])
        )
        assert resp.status_code == 403

    async def test_update_forbidden_member(self, client: AsyncClient, project_owner):
        """403 — member (нет project.settings.write)."""
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
        resp = await client.patch(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}",
            json={"name": "Member Updated"},
            headers=auth_headers(member["access_token"])
        )
        assert resp.status_code == 403

    async def test_update_not_found(self, client: AsyncClient, project_owner):
        """404 — несуществующий проект."""
        proj = project_owner
        resp = await client.patch(
            f"{API}/workspaces/{proj['ws_id']}/projects/00000000-0000-0000-0000-000000000000",
            json={"name": "Ghost"},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 404

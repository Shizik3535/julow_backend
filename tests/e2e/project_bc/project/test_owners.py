"""E2E-тесты: POST/DELETE /workspaces/{ws_id}/projects/{project_id}/owners — Управление владельцами проекта."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    register_and_login,
    add_project_member_with_role
)


@pytest.mark.e2e
class TestProjectOwners:
    """Управление владельцами проекта (project.*)."""

    async def test_add_owner_success(self, client: AsyncClient, project_owner):
        """200 — owner добавляет со-владельца."""
        proj = project_owner
        new_owner = await register_and_login(client)
        await add_project_member_with_role(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            owner_token=proj["access_token"],
            new_member_user_id=new_owner["user_id"],
            role_name="admin"
        )
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/owners",
            json={"user_id": new_owner["user_id"]},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 200

    async def test_add_owner_no_auth(self, client: AsyncClient, project_owner):
        """401 — без токена."""
        proj = project_owner
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/owners",
            json={"user_id": "some-user"}
        )
        assert resp.status_code == 401

    async def test_add_owner_forbidden_admin(self, client: AsyncClient, project_owner):
        """403 — admin (нет project.*)."""
        proj = project_owner
        admin = await register_and_login(client)
        other = await register_and_login(client)
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
            new_member_user_id=other["user_id"],
            role_name="member"
        )
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/owners",
            json={"user_id": other["user_id"]},
            headers=auth_headers(admin["access_token"])
        )
        assert resp.status_code == 403

    async def test_remove_owner_success(self, client: AsyncClient, project_owner):
        """200 — owner удаляет со-владельца."""
        proj = project_owner
        co_owner = await register_and_login(client)
        await add_project_member_with_role(
            client,
            ws_id=proj["ws_id"],
            project_id=proj["project_id"],
            owner_token=proj["access_token"],
            new_member_user_id=co_owner["user_id"],
            role_name="admin"
        )
        await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/owners",
            json={"user_id": co_owner["user_id"]},
            headers=auth_headers(proj["access_token"])
        )
        resp = await client.delete(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/owners/{co_owner['user_id']}",
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 200

    async def test_remove_owner_no_auth(self, client: AsyncClient, project_owner):
        """401 — без токена."""
        proj = project_owner
        resp = await client.delete(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/owners/{proj['user_id']}"
        )
        assert resp.status_code == 401

    async def test_remove_owner_forbidden_admin(self, client: AsyncClient, project_owner):
        """403 — admin (нет project.*)."""
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
        resp = await client.delete(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/owners/{proj['user_id']}",
            headers=auth_headers(admin["access_token"])
        )
        assert resp.status_code == 403

    async def test_add_owner_not_found(self, client: AsyncClient, project_owner):
        """404 — несуществующий проект."""
        proj = project_owner
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/00000000-0000-0000-0000-000000000000/owners",
            json={"user_id": "some-user"},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 404

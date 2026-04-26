"""E2E-тесты: POST /workspaces/{ws_id}/projects/{project_id}/restore — Восстановить проект."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    register_and_login,
    add_project_member_with_role
)


@pytest.mark.e2e
class TestRestoreProject:
    """Восстановить проект из архива (project.*)."""
    async def test_restore_no_auth(self, client: AsyncClient, project_owner):
        """401 — без токена."""
        proj = project_owner
        await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/archive",
            headers=auth_headers(proj["access_token"])
        )
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/restore"
        )
        assert resp.status_code == 401
    async def test_restore_not_found(self, client: AsyncClient, project_owner):
        """404 — несуществующий проект."""
        proj = project_owner
        user = await register_and_login(client)
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/00000000-0000-0000-0000-000000000000/restore",
            headers=auth_headers(user["access_token"])
        )
        assert resp.status_code == 404
    async def test_restore_idempotent_not_archived(self, client: AsyncClient, project_owner):
        """200 — restore на не-архивном проекте идемпотентен (без ошибки)."""
        proj = project_owner
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/restore",
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 200
    async def test_restore_success_owner(self, client: AsyncClient, project_owner):
        """200 — owner восстанавливает."""
        proj = project_owner
        await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/archive",
            headers=auth_headers(proj["access_token"])
        )
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/restore",
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 200
    async def test_restore_forbidden_admin(self, client: AsyncClient, project_owner):
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
        await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/archive",
            headers=auth_headers(proj["access_token"])
        )
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/restore",
            headers=auth_headers(admin["access_token"])
        )
        assert resp.status_code == 403

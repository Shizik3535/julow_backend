"""E2E-тесты: PATCH /workspaces/{ws_id}/projects/{project_id}/methodology — Смена методологии проекта."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    register_and_login,
    add_project_member_with_role
)


@pytest.mark.e2e
class TestChangeMethodology:
    """Смена методологии проекта (project.settings.write)."""

    async def test_change_methodology_success_owner(self, client: AsyncClient, project_owner):
        """200 — owner меняет методологию."""
        proj = project_owner
        resp = await client.patch(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/methodology",
            json={"new_methodology": "kanban"},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 200

    async def test_change_methodology_success_admin(self, client: AsyncClient, project_owner):
        """200 — admin меняет методологию (project.settings.*)."""
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
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/methodology",
            json={"new_methodology": "kanban"},
            headers=auth_headers(admin["access_token"])
        )
        assert resp.status_code == 200

    async def test_change_methodology_no_auth(self, client: AsyncClient, project_owner):
        """401 — без токена."""
        proj = project_owner
        resp = await client.patch(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/methodology",
            json={"new_methodology": "kanban"}
        )
        assert resp.status_code == 401

    async def test_change_methodology_forbidden_manager(self, client: AsyncClient, project_owner):
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
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/methodology",
            json={"new_methodology": "kanban"},
            headers=auth_headers(manager["access_token"])
        )
        assert resp.status_code == 403

    async def test_change_methodology_not_found(self, client: AsyncClient, project_owner):
        """404 — несуществующий проект."""
        proj = project_owner
        resp = await client.patch(
            f"{API}/workspaces/{proj['ws_id']}/projects/00000000-0000-0000-0000-000000000000/methodology",
            json={"new_methodology": "kanban"},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 404

    async def test_change_methodology_invalid(self, client: AsyncClient, project_owner):
        """422 — невалидная методология."""
        proj = project_owner
        resp = await client.patch(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/methodology",
            json={"new_methodology": "invalid"},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 422

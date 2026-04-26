"""E2E-тесты: PATCH/DELETE views и automations доски проекта."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    register_and_login,
    add_project_member_with_role
)


@pytest.mark.e2e
class TestBoardViews:
    """Представления доски (views.write)."""
    async def test_update_view_success_admin(self, client: AsyncClient, project_owner):
        """200 — admin обновляет представление (views.*)."""
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
        # Get board to find view id
        board_resp = await client.get(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/board",
            headers=auth_headers(proj["access_token"])
        )
        board_data = board_resp.json()["data"]
        views = board_data.get("views", [])
        if views:
            view_id = views[0]["id"]
            resp = await client.patch(
                f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/board/views/{view_id}",
                json={"name": "Updated View"},
                headers=auth_headers(admin["access_token"])
            )
            assert resp.status_code == 200
    async def test_update_view_forbidden_manager(self, client: AsyncClient, project_owner):
        """403 — manager (только views.read)."""
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
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/board/views/00000000-0000-0000-0000-000000000000",
            json={"name": "Forbidden"},
            headers=auth_headers(manager["access_token"])
        )
        assert resp.status_code == 403

    async def test_delete_view_success_admin(self, client: AsyncClient, project_owner):
        """200 — admin удаляет представление (views.*)."""
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
        views = board_data.get("views", [])
        if views:
            view_id = views[0]["id"]
            resp = await client.delete(
                f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/board/views/{view_id}",
                headers=auth_headers(admin["access_token"])
            )
            assert resp.status_code == 200

@pytest.mark.e2e
class TestBoardAutomations:
    """Автоматизации доски (automations.write)."""

    async def test_update_automation_success_admin(self, client: AsyncClient, project_owner):
        """200 — admin обновляет правило автоматизации (automations.*)."""
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
        automations = board_data.get("automation_rules", [])
        if automations:
            rule_id = automations[0]["id"]
            resp = await client.patch(
                f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/board/automations/{rule_id}",
                json={"name": "Updated Rule"},
                headers=auth_headers(admin["access_token"])
            )
            assert resp.status_code == 200

    async def test_remove_automation_success_admin(self, client: AsyncClient, project_owner):
        """200 — admin удаляет правило автоматизации."""
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
        automations = board_data.get("automation_rules", [])
        if automations:
            rule_id = automations[0]["id"]
            resp = await client.delete(
                f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/board/automations/{rule_id}",
                headers=auth_headers(admin["access_token"])
            )
            assert resp.status_code == 200

    async def test_update_automation_forbidden_manager(self, client: AsyncClient, project_owner):
        """403 — manager (нет automations.write)."""
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
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/board/automations/00000000-0000-0000-0000-000000000000",
            json={"name": "Forbidden"},
            headers=auth_headers(manager["access_token"])
        )
        assert resp.status_code == 403

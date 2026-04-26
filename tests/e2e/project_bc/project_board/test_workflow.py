"""E2E-тесты: CRUD workflow статусов и переходов доски проекта."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    register_and_login,
    add_project_member_with_role
)


@pytest.mark.e2e
class TestWorkflowStatuses:
    """Workflow статусы (workflow.write)."""

    async def test_add_status_success_admin(self, client: AsyncClient, project_owner):
        """201 — admin добавляет статус workflow (workflow.*)."""
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
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/board/workflow/statuses",
            json={"name": "In Review", "category": "review", "color": "#9B59B6"},
            headers=auth_headers(admin["access_token"])
        )
        assert resp.status_code == 201

    async def test_add_status_success_manager(self, client: AsyncClient, project_owner):
        """201 — manager добавляет статус workflow (workflow.*)."""
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
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/board/workflow/statuses",
            json={"name": "Blocked", "category": "blocked", "color": "#E74C3C"},
            headers=auth_headers(manager["access_token"])
        )
        assert resp.status_code == 201

    async def test_add_status_no_auth(self, client: AsyncClient, project_owner):
        """401 — без токена."""
        proj = project_owner
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/board/workflow/statuses",
            json={"name": "NoAuth", "category": "todo"}
        )
        assert resp.status_code == 401

    async def test_remove_status_success_admin(self, client: AsyncClient, project_owner):
        """200 — admin удаляет статус workflow."""
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
        # Add status first
        add_resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/board/workflow/statuses",
            json={"name": "To Delete", "category": "todo"},
            headers=auth_headers(proj["access_token"])
        )
        if add_resp.status_code == 201:
            status_id = add_resp.json().get("data", {}).get("id", "")
            if status_id:
                resp = await client.delete(
                    f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/board/workflow/statuses/{status_id}",
                    headers=auth_headers(admin["access_token"])
                )
                assert resp.status_code == 200


@pytest.mark.e2e
class TestWorkflowTransitions:
    """Workflow переходы (workflow.write)."""

    async def test_add_transition_success_admin(self, client: AsyncClient, project_owner):
        """201 — admin добавляет переход workflow."""
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
        # Get board to find existing statuses
        board_resp = await client.get(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/board",
            headers=auth_headers(proj["access_token"])
        )
        board_data = board_resp.json()["data"]
        statuses = board_data.get("workflow_statuses", [])
        if len(statuses) >= 2:
            from_id = statuses[0]["id"]
            to_id = statuses[1]["id"]
            resp = await client.post(
                f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/board/workflow/transitions",
                json={"from_status_id": from_id, "to_status_id": to_id, "name": "Start Work"},
                headers=auth_headers(admin["access_token"])
            )
            assert resp.status_code == 201

    async def test_add_transition_no_auth(self, client: AsyncClient, project_owner):
        """401 — без токена."""
        proj = project_owner
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/board/workflow/transitions",
            json={"from_status_id": "a", "to_status_id": "b", "name": "NoAuth"}
        )
        assert resp.status_code == 401

    async def test_remove_transition_success_admin(self, client: AsyncClient, project_owner):
        """200 — admin удаляет переход workflow."""
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
        transitions = board_data.get("workflow_transitions", [])
        if transitions:
            tid = transitions[0]["id"]
            resp = await client.delete(
                f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/board/workflow/transitions/{tid}",
                headers=auth_headers(admin["access_token"])
            )
            assert resp.status_code == 200

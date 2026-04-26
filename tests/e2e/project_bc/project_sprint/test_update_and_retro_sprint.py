"""E2E-тесты: PATCH goal/date-range, POST retro — Обновление спринта и ретроспектива."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    register_and_login,
    add_project_member_with_role
)


async def _create_sprint(client: AsyncClient, proj: dict) -> str:
    """Helper: create a sprint and return its ID."""
    resp = await client.post(
        f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/sprints",
        json={"name": "Sprint 1"},
        headers=auth_headers(proj["access_token"])
    )
    assert resp.status_code == 201
    return resp.json()["data"]["id"]


@pytest.mark.e2e
class TestUpdateSprintGoal:
    """Обновление цели спринта (sprints.write)."""

    async def test_update_goal_success_manager(self, client: AsyncClient, project_owner):
        """200 — manager обновляет цель спринта."""
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
        sprint_id = await _create_sprint(client, proj)
        resp = await client.patch(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/sprints/{sprint_id}/goal",
            json={"goal": "Ship auth feature"},
            headers=auth_headers(manager["access_token"])
        )
        assert resp.status_code == 200

    async def test_update_goal_forbidden_member(self, client: AsyncClient, project_owner):
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
        sprint_id = await _create_sprint(client, proj)
        resp = await client.patch(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/sprints/{sprint_id}/goal",
            json={"goal": "Forbidden"},
            headers=auth_headers(member["access_token"])
        )
        assert resp.status_code == 403


@pytest.mark.e2e
class TestUpdateSprintDateRange:
    """Обновление дат спринта (sprints.write)."""

    async def test_update_date_range_success_manager(self, client: AsyncClient, project_owner):
        """200 — manager обновляет даты спринта."""
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
        sprint_id = await _create_sprint(client, proj)
        resp = await client.patch(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/sprints/{sprint_id}/date-range",
            json={"start_date": "2026-05-01", "end_date": "2026-05-14"},
            headers=auth_headers(manager["access_token"])
        )
        assert resp.status_code == 200

    async def test_update_date_range_forbidden_member(self, client: AsyncClient, project_owner):
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
        sprint_id = await _create_sprint(client, proj)
        resp = await client.patch(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/sprints/{sprint_id}/date-range",
            json={"start_date": "2026-05-01", "end_date": "2026-05-14"},
            headers=auth_headers(member["access_token"])
        )
        assert resp.status_code == 403


@pytest.mark.e2e
class TestCreateSprintRetro:
    """Создание ретроспективы спринта (sprints.retro.write)."""

    async def test_create_retro_success_manager(self, client: AsyncClient, project_owner):
        """200 — manager создаёт ретроспективу (sprints.* → sprints.retro.write)."""
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
        sprint_id = await _create_sprint(client, proj)
        # Create a retro template via API
        template_resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/retro-templates/",
            json={
                "name": "Test Retro",
                "sections": [
                    {"title": "Went well", "prompt": "What went well?", "item_type": "positive"},
                    {"title": "To improve", "prompt": "What to improve?", "item_type": "negative"},
                    {"title": "Action items", "prompt": None, "item_type": "action_item"},
                ],
            },
            headers=auth_headers(proj["access_token"])
        )
        template_id = template_resp.json()["data"]["id"]
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/sprints/{sprint_id}/retro",
            json={"template_id": template_id},
            headers=auth_headers(manager["access_token"])
        )
        assert resp.status_code in (200, 201)

    async def test_create_retro_forbidden_member(self, client: AsyncClient, project_owner):
        """403 — member (нет sprints.retro.write)."""
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
        sprint_id = await _create_sprint(client, proj)
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/sprints/{sprint_id}/retro",
            json={"template_id": "00000000-0000-0000-0000-000000000000"},
            headers=auth_headers(member["access_token"])
        )
        assert resp.status_code == 403

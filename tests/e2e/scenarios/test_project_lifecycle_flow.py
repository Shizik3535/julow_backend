"""E2E-сценарий: полный жизненный цикл проекта — создание, настройка, работа, архивация."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    create_project,
    register_and_login,
    add_project_member_with_role,
    add_ws_member_with_role
)


@pytest.mark.e2e
class TestProjectLifecycleFlow:
    """
    Многошаговый сценарий:
    1. Создать workspace и проект (hybrid)
    2. Добавить участников с разными ролями
    3. Создать кастомную роль
    4. Создать эпик и спринт
    5. Запустить спринт
    6. Добавить milestone
    7. Изменить видимость проекта
    8. Архивировать проект
    9. Восстановить проект
    10. Приостановить и реактивировать проект
    """

    async def test_full_project_lifecycle(self, client: AsyncClient, workspace_owner):
        """Полный жизненный цикл проекта от создания до архивации и восстановления."""
        # 1. Создать workspace и проект
        ws = workspace_owner
        proj = await create_project(
            client, ws_id=ws["ws_id"], token=ws["access_token"], methodology="hybrid"
        )
        project_id = proj["project_id"]
        ws_id = ws["ws_id"]
        owner_token = ws["access_token"]

        # Verify project created
        get_resp = await client.get(
            f"{API}/workspaces/{ws_id}/projects/{project_id}",
            headers=auth_headers(owner_token)
        )
        assert get_resp.status_code == 200
        assert get_resp.json()["data"]["methodology"] == "hybrid"
        assert get_resp.json()["data"]["status"] == "active"

        # 2. Добавить участников
        admin = await register_and_login(client)
        manager = await register_and_login(client)
        member_user = await register_and_login(client)

        await add_project_member_with_role(
            client, ws_id=ws_id, project_id=project_id,
            owner_token=owner_token, new_member_user_id=admin["user_id"], role_name="admin"
        )
        await add_project_member_with_role(
            client, ws_id=ws_id, project_id=project_id,
            owner_token=owner_token, new_member_user_id=manager["user_id"], role_name="manager"
        )
        await add_project_member_with_role(
            client, ws_id=ws_id, project_id=project_id,
            owner_token=owner_token, new_member_user_id=member_user["user_id"], role_name="member"
        )

        # Verify members count
        members_resp = await client.get(
            f"{API}/workspaces/{ws_id}/projects/{project_id}/members",
            headers=auth_headers(owner_token)
        )
        assert members_resp.status_code == 200
        assert len(members_resp.json()["data"]) >= 4

        # 3. Создать кастомную роль
        role_resp = await client.post(
            f"{API}/workspaces/{ws_id}/projects/{project_id}/roles",
            json={"name": "Developer", "permissions": ["tasks.read", "tasks.create", "tasks.update"], "description": "Dev role"},
            headers=auth_headers(admin["access_token"])
        )
        assert role_resp.status_code == 201

        # 4. Создать эпик
        epic_resp = await client.post(
            f"{API}/workspaces/{ws_id}/projects/{project_id}/epics",
            json={"name": "Authentication Module"},
            headers=auth_headers(manager["access_token"])
        )
        assert epic_resp.status_code == 201
        epic_id = epic_resp.json()["data"]["id"]

        # 5. Создать и запустить спринт
        sprint_resp = await client.post(
            f"{API}/workspaces/{ws_id}/projects/{project_id}/sprints",
            json={"name": "Sprint 1", "goal": "Implement auth"},
            headers=auth_headers(manager["access_token"])
        )
        assert sprint_resp.status_code == 201
        sprint_id = sprint_resp.json()["data"]["id"]

        start_resp = await client.post(
            f"{API}/workspaces/{ws_id}/projects/{project_id}/sprints/{sprint_id}/start",
            headers=auth_headers(manager["access_token"])
        )
        assert start_resp.status_code == 200

        # Verify active sprint
        active_resp = await client.get(
            f"{API}/workspaces/{ws_id}/projects/{project_id}/sprints/active",
            headers=auth_headers(owner_token)
        )
        assert active_resp.status_code == 200

        # Complete the sprint before further operations
        complete_resp = await client.post(
            f"{API}/workspaces/{ws_id}/projects/{project_id}/sprints/{sprint_id}/complete",
            headers=auth_headers(manager["access_token"])
        )
        assert complete_resp.status_code == 200

        # 6. Добавить milestone
        ms_resp = await client.post(
            f"{API}/workspaces/{ws_id}/projects/{project_id}/milestones",
            json={"name": "v1.0 Release", "due_date": "2026-12-31"},
            headers=auth_headers(manager["access_token"])
        )
        assert ms_resp.status_code == 201
        ms_id = ms_resp.json()["data"]["id"]

        # Change milestone status
        ms_status_resp = await client.post(
            f"{API}/workspaces/{ws_id}/projects/{project_id}/milestones/{ms_id}/change-status",
            json={"new_status": "in_progress"},
            headers=auth_headers(manager["access_token"])
        )
        assert ms_status_resp.status_code == 200

        # 7. Изменить видимость (admin)
        vis_resp = await client.patch(
            f"{API}/workspaces/{ws_id}/projects/{project_id}/visibility",
            json={"visibility": "workspace"},
            headers=auth_headers(admin["access_token"])
        )
        assert vis_resp.status_code == 200

        # 8. Архивировать проект (owner only)
        archive_resp = await client.post(
            f"{API}/workspaces/{ws_id}/projects/{project_id}/archive",
            headers=auth_headers(owner_token)
        )
        assert archive_resp.status_code == 200

        # Verify status
        get_resp = await client.get(
            f"{API}/workspaces/{ws_id}/projects/{project_id}",
            headers=auth_headers(owner_token)
        )
        assert get_resp.json()["data"]["status"] == "archived"

        # 9. Восстановить проект (owner only)
        restore_resp = await client.post(
            f"{API}/workspaces/{ws_id}/projects/{project_id}/restore",
            headers=auth_headers(owner_token)
        )
        assert restore_resp.status_code == 200

        get_resp = await client.get(
            f"{API}/workspaces/{ws_id}/projects/{project_id}",
            headers=auth_headers(owner_token)
        )
        assert get_resp.json()["data"]["status"] == "active"

        # 10. Приостановить и реактивировать
        suspend_resp = await client.post(
            f"{API}/workspaces/{ws_id}/projects/{project_id}/suspend",
            json={"reason": "Maintenance"},
            headers=auth_headers(owner_token)
        )
        assert suspend_resp.status_code == 200

        reactivate_resp = await client.post(
            f"{API}/workspaces/{ws_id}/projects/{project_id}/reactivate",
            headers=auth_headers(owner_token)
        )
        assert reactivate_resp.status_code == 200

        get_resp = await client.get(
            f"{API}/workspaces/{ws_id}/projects/{project_id}",
            headers=auth_headers(owner_token)
        )
        assert get_resp.json()["data"]["status"] == "active"


@pytest.mark.e2e
class TestProjectPermissionCascadeFlow:
    """
    Сценарий проверки каскадирования permissions:
    workspace admin может создавать проекты,
    но project member не может управлять проектом.
    """

    async def test_ws_admin_can_create_project(self, client: AsyncClient, workspace_owner):
        """ws admin может создавать проекты в workspace."""
        ws = workspace_owner
        ws_admin = await register_and_login(client)
        await add_ws_member_with_role(
            client,
            ws_id=ws["ws_id"],
            owner_token=ws["access_token"],
            new_member_user_id=ws_admin["user_id"],
            role_name="admin"
        )
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/projects/",
            json={"name": "Admin Project", "methodology": "kanban"},
            headers=auth_headers(ws_admin["access_token"])
        )
        assert resp.status_code == 201

    async def test_project_guest_cannot_read_members(self, client: AsyncClient, workspace_owner):
        """project guest не может читать участников (нет members.read)."""
        ws = workspace_owner
        proj = await create_project(client, ws_id=ws["ws_id"], token=ws["access_token"])
        guest = await register_and_login(client)
        await add_project_member_with_role(
            client,
            ws_id=ws["ws_id"],
            project_id=proj["project_id"],
            owner_token=ws["access_token"],
            new_member_user_id=guest["user_id"],
            role_name="guest"
        )
        resp = await client.get(
            f"{API}/workspaces/{ws['ws_id']}/projects/{proj['project_id']}/members",
            headers=auth_headers(guest["access_token"])
        )
        assert resp.status_code == 403

    async def test_non_member_cannot_access_project(self, client: AsyncClient, workspace_owner):
        """Пользователь не участник проекта получает 403."""
        ws = workspace_owner
        proj = await create_project(client, ws_id=ws["ws_id"], token=ws["access_token"])
        stranger = await register_and_login(client)
        resp = await client.get(
            f"{API}/workspaces/{ws['ws_id']}/projects/{proj['project_id']}",
            headers=auth_headers(stranger["access_token"])
        )
        assert resp.status_code == 403

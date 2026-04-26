"""E2E-тесты: POST /workspaces/{ws_id}/projects/ — Создание проекта."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    register_and_login,
    add_ws_member_with_role
)


@pytest.mark.e2e
class TestCreateProject:
    """Создание проекта (ws.projects.create)."""

    async def test_create_success(self, client: AsyncClient, workspace_owner):
        """201 — проект создан, текущий пользователь — владелец."""
        ws = workspace_owner
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/projects/",
            json={"name": "Test Project", "methodology": "scrum"},
            headers=auth_headers(ws["access_token"])
        )
        assert resp.status_code == 201
        data = resp.json()["data"]
        assert data["id"]
        assert data["name"] == "Test Project"
        assert data["methodology"] == "scrum"
        assert data["status"] == "active"
        assert ws["user_id"] in data["owner_ids"]

    async def test_create_with_kanban(self, client: AsyncClient, workspace_owner):
        """201 — проект с методологией kanban."""
        ws = workspace_owner
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/projects/",
            json={"name": "Kanban Project", "methodology": "kanban"},
            headers=auth_headers(ws["access_token"])
        )
        assert resp.status_code == 201
        data = resp.json()["data"]
        assert data["methodology"] == "kanban"

    async def test_create_no_auth(self, client: AsyncClient, workspace_owner):
        """401 — без токена авторизации."""
        ws = workspace_owner
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/projects/",
            json={"name": "NoAuth Project", "methodology": "scrum"}
        )
        assert resp.status_code == 401

    async def test_create_forbidden_non_ws_member(self, client: AsyncClient, workspace_owner):
        """403 — пользователь не участник workspace."""
        ws = workspace_owner
        stranger = await register_and_login(client)
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/projects/",
            json={"name": "Forbidden Project", "methodology": "scrum"},
            headers=auth_headers(stranger["access_token"])
        )
        assert resp.status_code == 403

    async def test_create_validation_empty_name(self, client: AsyncClient, workspace_owner):
        """422 — пустое название проекта."""
        ws = workspace_owner
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/projects/",
            json={"name": "", "methodology": "scrum"},
            headers=auth_headers(ws["access_token"])
        )
        assert resp.status_code == 422

    async def test_create_validation_short_name(self, client: AsyncClient, workspace_owner):
        """422 — название < 3 символов."""
        ws = workspace_owner
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/projects/",
            json={"name": "AB", "methodology": "scrum"},
            headers=auth_headers(ws["access_token"])
        )
        assert resp.status_code == 422

    async def test_create_validation_missing_body(self, client: AsyncClient, workspace_owner):
        """422 — отсутствует тело запроса."""
        ws = workspace_owner
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/projects/",
            headers=auth_headers(ws["access_token"])
        )
        assert resp.status_code == 422

    async def test_create_validation_invalid_methodology(self, client: AsyncClient, workspace_owner):
        """422 — невалидная методология."""
        ws = workspace_owner
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/projects/",
            json={"name": "Bad Method", "methodology": "invalid"},
            headers=auth_headers(ws["access_token"])
        )
        assert resp.status_code == 422

    async def test_create_ws_member_with_projects_create(self, client: AsyncClient, workspace_owner):
        """201 — ws admin может создавать проекты (ws.projects.create)."""
        ws = workspace_owner
        admin = await register_and_login(client)
        await add_ws_member_with_role(
            client,
            ws_id=ws["ws_id"],
            owner_token=ws["access_token"],
            new_member_user_id=admin["user_id"],
            role_name="admin"
        )
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/projects/",
            json={"name": "Admin Project", "methodology": "scrum"},
            headers=auth_headers(admin["access_token"])
        )
        assert resp.status_code == 201

"""E2E-тесты: GET /workspaces/{ws_id}/projects/ — Список проектов."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    create_project,
    register_and_login
)


@pytest.mark.e2e
class TestListProjects:
    """Список проектов workspace (project.read)."""
    async def test_list_success(self, client: AsyncClient, workspace_owner):
        """200 — список проектов workspace."""
        ws = workspace_owner
        await create_project(client, ws_id=ws["ws_id"], token=ws["access_token"])
        resp = await client.get(
            f"{API}/workspaces/{ws['ws_id']}/projects/",
            headers=auth_headers(ws["access_token"])
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert isinstance(data, list)
        assert len(data) >= 1
    async def test_list_archived_has_archived(self, client: AsyncClient, workspace_owner):
        """200 — архивированные проекты (1 проект после архивации)."""
        ws = workspace_owner
        proj = await create_project(client, ws_id=ws["ws_id"], token=ws["access_token"])
        await client.post(
            f"{API}/workspaces/{ws['ws_id']}/projects/{proj['project_id']}/archive",
            headers=auth_headers(ws["access_token"])
        )
        resp = await client.get(
            f"{API}/workspaces/{ws['ws_id']}/projects/archived",
            headers=auth_headers(ws["access_token"])
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert len(data) >= 1
    async def test_list_no_auth(self, client: AsyncClient, workspace_owner):
        """401 — без токена."""
        ws = workspace_owner
        resp = await client.get(
            f"{API}/workspaces/{ws['ws_id']}/projects/"
        )
        assert resp.status_code == 401
    async def test_list_empty_for_non_ws_member(self, client: AsyncClient, workspace_owner):
        """200 — не участник workspace получает пустой список."""
        ws = workspace_owner
        stranger = await register_and_login(client)
        resp = await client.get(
            f"{API}/workspaces/{ws['ws_id']}/projects/",
            headers=auth_headers(stranger["access_token"])
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert isinstance(data, list)
        assert len(data) == 0
    async def test_list_archived_success(self, client: AsyncClient, workspace_owner):
        """200 — архивированные проекты (пустой список)."""
        ws = workspace_owner
        await create_project(client, ws_id=ws["ws_id"], token=ws["access_token"])
        resp = await client.get(
            f"{API}/workspaces/{ws['ws_id']}/projects/archived",
            headers=auth_headers(ws["access_token"])
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert isinstance(data, list)

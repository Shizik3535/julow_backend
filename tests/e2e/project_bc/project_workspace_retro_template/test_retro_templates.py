"""E2E-тесты: CRUD шаблонов ретроспектив workspace."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    register_and_login,
    add_ws_member_with_role
)


RETRO_SECTIONS = [
    {"title": "What went well", "item_type": "positive"},
    {"title": "What to improve", "item_type": "negative"},
    {"title": "Action items", "item_type": "action_item"},
]


@pytest.mark.e2e
class TestWorkspaceRetroTemplates:
    """Шаблоны ретроспектив workspace (projects.retro_templates.write)."""
    async def test_list_templates_success(self, client: AsyncClient, workspace_owner):
        """200 — список шаблонов workspace (без авторизации)."""
        ws = workspace_owner
        resp = await client.get(
            f"{API}/workspaces/{ws['ws_id']}/retro-templates/"
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert isinstance(data, list)
    async def test_create_template_success_ws_admin(self, client: AsyncClient, workspace_owner):
        """201 — ws admin создаёт шаблон (projects.retro_templates.write)."""
        ws = workspace_owner
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/retro-templates/",
            json={"name": "Standard Retro", "sections": RETRO_SECTIONS},
            headers=auth_headers(ws["access_token"])
        )
        assert resp.status_code == 201
        data = resp.json()["data"]
        assert data["id"]
        assert data["name"] == "Standard Retro"
    async def test_create_template_no_auth(self, client: AsyncClient, workspace_owner):
        """401 — без токена."""
        ws = workspace_owner
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/retro-templates/",
            json={"name": "NoAuth Retro", "sections": RETRO_SECTIONS}
        )
        assert resp.status_code == 401
    async def test_create_template_forbidden_ws_member(self, client: AsyncClient, workspace_owner):
        """403 — ws member (нет projects.retro_templates.write)."""
        ws = workspace_owner
        member = await register_and_login(client)
        await add_ws_member_with_role(
            client,
            ws_id=ws["ws_id"],
            owner_token=ws["access_token"],
            new_member_user_id=member["user_id"],
            role_name="member"
        )
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/retro-templates/",
            json={"name": "Forbidden Retro", "sections": RETRO_SECTIONS},
            headers=auth_headers(member["access_token"])
        )
        assert resp.status_code == 403
    async def test_update_template_success_ws_admin(self, client: AsyncClient, workspace_owner):
        """200 — ws admin обновляет шаблон."""
        ws = workspace_owner
        create_resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/retro-templates/",
            json={"name": "Retro V1", "sections": RETRO_SECTIONS},
            headers=auth_headers(ws["access_token"])
        )
        assert create_resp.status_code == 201
        template_id = create_resp.json()["data"]["id"]
        resp = await client.patch(
            f"{API}/workspaces/{ws['ws_id']}/retro-templates/{template_id}",
            json={"sections": [{"title": "New Section", "item_type": "neutral"}]},
            headers=auth_headers(ws["access_token"])
        )
        assert resp.status_code == 200
    async def test_update_template_no_auth(self, client: AsyncClient, workspace_owner):
        """401 — без токена."""
        ws = workspace_owner
        resp = await client.patch(
            f"{API}/workspaces/{ws['ws_id']}/retro-templates/00000000-0000-0000-0000-000000000000",
            json={"sections": [{"title": "X", "item_type": "neutral"}]}
        )
        assert resp.status_code == 401
    async def test_delete_template_no_auth(self, client: AsyncClient, workspace_owner):
        """401 — без токена."""
        ws = workspace_owner
        resp = await client.delete(
            f"{API}/workspaces/{ws['ws_id']}/retro-templates/00000000-0000-0000-0000-000000000000"
        )
        assert resp.status_code == 401
    async def test_create_template_validation_empty_name(self, client: AsyncClient, workspace_owner):
        """422 — пустое название шаблона."""
        ws = workspace_owner
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/retro-templates/",
            json={"name": "", "sections": RETRO_SECTIONS},
            headers=auth_headers(ws["access_token"])
        )
        assert resp.status_code == 422
    async def test_delete_template_success_ws_admin(self, client: AsyncClient, workspace_owner):
        """200 — ws admin удаляет шаблон."""
        ws = workspace_owner
        create_resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/retro-templates/",
            json={"name": "To Delete", "sections": RETRO_SECTIONS},
            headers=auth_headers(ws["access_token"])
        )
        assert create_resp.status_code == 201
        template_id = create_resp.json()["data"]["id"]
        resp = await client.delete(
            f"{API}/workspaces/{ws['ws_id']}/retro-templates/{template_id}",
            headers=auth_headers(ws["access_token"])
        )
        assert resp.status_code == 200

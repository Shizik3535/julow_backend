"""E2E-тесты: CRUD кастомных полей проекта."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    register_and_login,
    add_project_member_with_role
)


@pytest.mark.e2e
class TestCustomFields:
    """Кастомные поля проекта (custom_fields.write)."""

    async def test_add_custom_field_success(self, client: AsyncClient, project_owner):
        """200 — admin добавляет кастомное поле (custom_fields.*)."""
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
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/custom-fields",
            json={"name": "Priority", "field_type": "select", "options": ["Low", "Medium", "High"]},
            headers=auth_headers(admin["access_token"])
        )
        assert resp.status_code in (200, 201)

    async def test_add_custom_field_success_owner(self, client: AsyncClient, project_owner):
        """200 — owner добавляет кастомное поле (project.*)."""
        proj = project_owner
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/custom-fields",
            json={"name": "Severity", "field_type": "select", "options": ["Low", "Medium", "High"]},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 200

    async def test_update_custom_field_success(self, client: AsyncClient, project_owner):
        """200 — admin обновляет кастомное поле."""
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
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/custom-fields",
            json={"name": "Category", "field_type": "select", "options": ["Low", "Medium", "High"]},
            headers=auth_headers(proj["access_token"])
        )
        resp = await client.patch(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/custom-fields/Category",
            json={"new_name": "Urgency", "options": ["Low", "Medium", "High", "Critical"]},
            headers=auth_headers(admin["access_token"])
        )
        assert resp.status_code == 200

    async def test_remove_custom_field_success(self, client: AsyncClient, project_owner):
        """200 — admin удаляет кастомное поле."""
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
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/custom-fields",
            json={"name": "Label", "field_type": "text"},
            headers=auth_headers(proj["access_token"])
        )
        resp = await client.delete(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/custom-fields/Label",
            headers=auth_headers(admin["access_token"])
        )
        assert resp.status_code == 200

    async def test_add_custom_field_forbidden_manager(self, client: AsyncClient, project_owner):
        """403 — manager (нет custom_fields.write)."""
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
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/custom-fields",
            json={"name": "BlockedField", "field_type": "text"},
            headers=auth_headers(manager["access_token"])
        )
        assert resp.status_code == 403

    async def test_add_custom_field_no_auth(self, client: AsyncClient, project_owner):
        """401 — без токена."""
        proj = project_owner
        resp = await client.post(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/custom-fields",
            json={"name": "NoAuthField", "field_type": "text"}
        )
        assert resp.status_code == 401

    async def test_update_custom_field_not_found(self, client: AsyncClient, project_owner):
        """404 — несуществующее кастомное поле."""
        proj = project_owner
        resp = await client.patch(
            f"{API}/workspaces/{proj['ws_id']}/projects/{proj['project_id']}/custom-fields/NonExistent",
            json={"new_name": "New"},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 404

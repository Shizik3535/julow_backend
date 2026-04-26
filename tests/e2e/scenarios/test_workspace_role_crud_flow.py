import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers
)


@pytest.mark.e2e
class TestWorkspaceRoleCrudFlow:
    """Сценарий: create_role → get_roles → update_role → get_role → delete_role → get_roles (нет кастомной)."""

    async def test_full_role_crud(self, client: AsyncClient, workspace_owner):
        ws = workspace_owner
        h = auth_headers(ws["access_token"])
        ws_id = ws["ws_id"]

        # 1. Create role
        resp = await client.post(
            f"{API}/workspaces/{ws_id}/roles",
            json={"name": "flow-role", "permissions": ["members.read"], "description": "Test role"},
            headers=h
        )
        assert resp.status_code == 201
        role_id = resp.json()["data"]["id"]

        # 2. Get roles — должна быть кастомная
        resp = await client.get(f"{API}/workspaces/{ws_id}/roles", headers=h)
        assert resp.status_code == 200
        items = resp.json()["items"]
        role_names = [r["name"] for r in items]
        assert "flow-role" in role_names

        # 3. Update role
        resp = await client.patch(
            f"{API}/workspaces/{ws_id}/roles/{role_id}",
            json={"permissions": ["members.read", "members.write"], "description": "Updated"},
            headers=h
        )
        assert resp.status_code == 200

        # 4. Get role
        resp = await client.get(f"{API}/workspaces/{ws_id}/roles/{role_id}", headers=h)
        assert resp.status_code == 200
        assert resp.json()["data"]["id"] == role_id

        # 5. Delete role
        resp = await client.delete(f"{API}/workspaces/{ws_id}/roles/{role_id}", headers=h)
        assert resp.status_code == 200

        # 6. Get roles — кастомной нет
        resp = await client.get(f"{API}/workspaces/{ws_id}/roles", headers=h)
        assert resp.status_code == 200
        items = resp.json()["items"]
        role_names = [r["name"] for r in items]
        assert "flow-role" not in role_names

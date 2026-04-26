"""E2E-сценарий: CRUD ролей организации."""

import pytest

from tests.e2e.conftest import API, auth_headers


@pytest.mark.e2e
class TestOrgRoleCrudFlow:
    """Сценарий: get_roles (system) → create → get → update → delete → get_roles (no custom)."""

    async def test_org_role_crud_flow(self, client, org_with_owner) -> None:
        """Полный CRUD-цикл кастомной роли."""
        owner = org_with_owner
        org_id = owner["org_id"]
        token = owner["access_token"]

        # 1. Список ролей — только системные
        resp = await client.get(
            f"{API}/orgs/{org_id}/roles",
            headers=auth_headers(token)
        )
        assert resp.status_code == 200
        initial_count = len(resp.json()["data"])

        # 2. Создание кастомной роли
        resp = await client.post(
            f"{API}/orgs/{org_id}/roles",
            json={
                "name": "Custom CRUD Role",
                "permissions": ["members:read"],
                "scope": "org",
            },
            headers=auth_headers(token)
        )
        assert resp.status_code == 201
        role_id = resp.json()["data"]["id"]

        # 3. Получение роли
        resp = await client.get(
            f"{API}/orgs/{org_id}/roles/{role_id}",
            headers=auth_headers(token)
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["name"] == "Custom CRUD Role"

        # 4. Обновление роли
        resp = await client.patch(
            f"{API}/orgs/{org_id}/roles/{role_id}",
            json={"permissions": ["members:read", "members:write"], "description": "Updated"},
            headers=auth_headers(token)
        )
        assert resp.status_code == 200

        # 5. Удаление роли
        resp = await client.delete(
            f"{API}/orgs/{org_id}/roles/{role_id}",
            headers=auth_headers(token)
        )
        assert resp.status_code == 200

        # 6. Список ролей — кастомной больше нет
        resp = await client.get(
            f"{API}/orgs/{org_id}/roles",
            headers=auth_headers(token)
        )
        assert resp.status_code == 200
        assert len(resp.json()["data"]) == initial_count

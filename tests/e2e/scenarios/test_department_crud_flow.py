"""E2E-сценарий: CRUD подразделений организации."""

import pytest

from tests.e2e.conftest import (
    API,
    add_member_to_org,
    auth_headers,
    register_and_login
)


@pytest.mark.e2e
class TestDepartmentCrudFlow:
    """Сценарий: create → get → update → add_member → remove_member → delete."""

    async def test_department_crud_flow(self, client, org_with_owner) -> None:
        """Полный CRUD-цикл подразделения с участником."""
        owner = org_with_owner
        org_id = owner["org_id"]
        token = owner["access_token"]

        # 1. Создание подразделения
        resp = await client.post(
            f"{API}/orgs/{org_id}/departments",
            json={"name": "Engineering"},
            headers=auth_headers(token)
        )
        assert resp.status_code == 201
        dept_id = resp.json()["data"]["id"]

        # 2. Получение подразделения
        resp = await client.get(
            f"{API}/orgs/{org_id}/departments/{dept_id}",
            headers=auth_headers(token)
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["name"] == "Engineering"

        # 3. Обновление подразделения
        resp = await client.patch(
            f"{API}/orgs/{org_id}/departments/{dept_id}",
            json={"name": "Platform Engineering"},
            headers=auth_headers(token)
        )
        assert resp.status_code == 200

        # 4. Добавление участника в орг и подразделение
        member = await register_and_login(client)
        await add_member_to_org(
            client,
            org_id=org_id,
            owner_token=token,
            new_member_user_id=member["user_id"]
        )
        resp = await client.post(
            f"{API}/orgs/{org_id}/departments/{dept_id}/members/{member['user_id']}",
            headers=auth_headers(token)
        )
        assert resp.status_code == 200

        # 5. Удаление участника из подразделения
        resp = await client.delete(
            f"{API}/orgs/{org_id}/departments/{dept_id}/members/{member['user_id']}",
            headers=auth_headers(token)
        )
        assert resp.status_code == 200

        # 6. Удаление подразделения
        resp = await client.delete(
            f"{API}/orgs/{org_id}/departments/{dept_id}",
            headers=auth_headers(token)
        )
        assert resp.status_code == 200

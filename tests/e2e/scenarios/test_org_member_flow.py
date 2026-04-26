"""E2E-сценарий: управление участниками организации."""

import pytest

from tests.e2e.conftest import (
    API,
    add_member_to_org,
    auth_headers,
    register_and_login
)


@pytest.mark.e2e
class TestOrgMemberFlow:
    """Сценарий: add_member → get_members → deactivate → reactivate → change_role → remove."""

    async def test_org_member_flow(self, client, org_with_owner) -> None:
        """Полный цикл управления участником."""
        owner = org_with_owner
        org_id = owner["org_id"]
        token = owner["access_token"]

        # 1. Добавление участника
        member = await register_and_login(client)
        await add_member_to_org(
            client,
            org_id=org_id,
            owner_token=token,
            new_member_user_id=member["user_id"]
        )

        # 2. Проверка в списке участников
        resp = await client.get(
            f"{API}/orgs/{org_id}/members",
            headers=auth_headers(token)
        )
        assert resp.status_code == 200
        member_ids = [m["user_id"] for m in resp.json()["data"]]
        assert member["user_id"] in member_ids

        # 3. Деактивация
        resp = await client.post(
            f"{API}/orgs/{org_id}/members/{member['user_id']}/deactivate",
            headers=auth_headers(token)
        )
        assert resp.status_code == 200

        # 4. Реактивация
        resp = await client.post(
            f"{API}/orgs/{org_id}/members/{member['user_id']}/reactivate",
            headers=auth_headers(token)
        )
        assert resp.status_code == 200

        # 5. Удаление участника
        resp = await client.delete(
            f"{API}/orgs/{org_id}/members/{member['user_id']}",
            headers=auth_headers(token)
        )
        assert resp.status_code == 200

        # 6. Проверка — участника больше нет
        resp = await client.get(
            f"{API}/orgs/{org_id}/members",
            headers=auth_headers(token)
        )
        member_ids = [m["user_id"] for m in resp.json()["data"]]
        assert member["user_id"] not in member_ids

"""E2E-сценарий: жизненный цикл команды."""

import pytest

from tests.e2e.conftest import (
    API,
    add_member_to_org,
    auth_headers,
    register_and_login
)


@pytest.mark.e2e
class TestTeamLifecycleFlow:
    """Сценарий: create_team → get → update → add_member → deactivate → reactivate → remove_member."""

    async def test_team_lifecycle_flow(self, client, org_with_owner) -> None:
        """Полный жизненный цикл команды с участником."""
        owner = org_with_owner
        org_id = owner["org_id"]
        token = owner["access_token"]

        # 1. Создание команды
        resp = await client.post(
            f"{API}/orgs/{org_id}/teams",
            json={"name": "Lifecycle Team"},
            headers=auth_headers(token)
        )
        assert resp.status_code == 201
        team_id = resp.json()["data"]["id"]

        # 2. Получение команды
        resp = await client.get(
            f"{API}/orgs/{org_id}/teams/{team_id}",
            headers=auth_headers(token)
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["name"] == "Lifecycle Team"

        # 3. Обновление команды
        resp = await client.patch(
            f"{API}/orgs/{org_id}/teams/{team_id}",
            json={"name": "Updated Team", "description": "After update"},
            headers=auth_headers(token)
        )
        assert resp.status_code == 200

        # 4. Добавление участника в орг и команду
        member = await register_and_login(client)
        await add_member_to_org(
            client,
            org_id=org_id,
            owner_token=token,
            new_member_user_id=member["user_id"]
        )
        resp = await client.post(
            f"{API}/orgs/{org_id}/teams/{team_id}/members/{member['user_id']}",
            headers=auth_headers(token)
        )
        assert resp.status_code == 200

        # 5. Деактивация команды
        resp = await client.post(
            f"{API}/orgs/{org_id}/teams/{team_id}/deactivate",
            headers=auth_headers(token)
        )
        assert resp.status_code == 200

        # 6. Реактивация команды
        resp = await client.post(
            f"{API}/orgs/{org_id}/teams/{team_id}/reactivate",
            headers=auth_headers(token)
        )
        assert resp.status_code == 200

        # 7. Удаление участника из команды
        resp = await client.delete(
            f"{API}/orgs/{org_id}/teams/{team_id}/members/{member['user_id']}",
            headers=auth_headers(token)
        )
        assert resp.status_code == 200

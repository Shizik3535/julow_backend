"""E2E-сценарий: жизненный цикл организации."""

import pytest

from tests.e2e.conftest import API, auth_headers


@pytest.mark.e2e
class TestOrgLifecycleFlow:
    """Сценарий: create → get → update_info → suspend → reactivate → request_deletion."""

    async def test_org_lifecycle_flow(self, client, org_with_owner) -> None:
        """Полный жизненный цикл организации."""
        # 1. Создание
        owner = org_with_owner
        org_id = owner["org_id"]
        token = owner["access_token"]

        # 2. Получение
        resp = await client.get(
            f"{API}/orgs/{org_id}",
            headers=auth_headers(token)
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["status"] == "active"

        # 3. Обновление информации
        resp = await client.patch(
            f"{API}/orgs/{org_id}",
            json={"name": "Updated Lifecycle Org"},
            headers=auth_headers(token)
        )
        assert resp.status_code == 200

        # 4. Приостановка
        resp = await client.post(
            f"{API}/orgs/{org_id}/suspend",
            json={"reason": "Scheduled maintenance"},
            headers=auth_headers(token)
        )
        assert resp.status_code == 200

        # Проверка статуса
        resp = await client.get(
            f"{API}/orgs/{org_id}",
            headers=auth_headers(token)
        )
        assert resp.json()["data"]["status"] == "suspended"

        # 5. Реактивация
        resp = await client.post(
            f"{API}/orgs/{org_id}/reactivate",
            headers=auth_headers(token)
        )
        assert resp.status_code == 200

        # Проверка статуса
        resp = await client.get(
            f"{API}/orgs/{org_id}",
            headers=auth_headers(token)
        )
        assert resp.json()["data"]["status"] == "active"

        # 6. Запрос удаления
        resp = await client.post(
            f"{API}/orgs/{org_id}/request-deletion",
            headers=auth_headers(token)
        )
        assert resp.status_code == 200

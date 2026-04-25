"""E2E-сценарий: SSO-интеграции организации."""

import uuid

import pytest

from tests.e2e.conftest import API, auth_headers, create_org_with_owner


@pytest.mark.e2e
class TestSSOIntegrationFlow:
    """Сценарий: add_sso → get_list → update → deactivate → get_list (deactivated)."""

    async def test_sso_integration_flow(self, client) -> None:
        """Полный цикл SSO-интеграции."""
        owner = await create_org_with_owner(client)
        org_id = owner["org_id"]
        token = owner["access_token"]

        # 1. Добавление SSO-интеграции
        entity_id = f"https://idp.example.com/{uuid.uuid4().hex[:8]}"
        resp = await client.post(
            f"{API}/orgs/{org_id}/sso-integrations",
            json={
                "provider": "saml",
                "entity_id": entity_id,
                "sso_url": "https://idp.example.com/sso",
                "certificate": "MIICpDCCAYwCCQDU+jh+",
            },
            headers=auth_headers(token),
        )
        assert resp.status_code == 201
        integration_id = resp.json()["data"]["id"]

        # 2. Проверка в списке интеграций
        resp = await client.get(
            f"{API}/orgs/{org_id}/sso-integrations",
            headers=auth_headers(token),
        )
        assert resp.status_code == 200
        integration_ids = [i["id"] for i in resp.json()["data"]]
        assert integration_id in integration_ids

        # 3. Обновление SSO-интеграции
        resp = await client.patch(
            f"{API}/orgs/{org_id}/sso-integrations/{integration_id}",
            json={"sso_url": "https://new-idp.example.com/sso"},
            headers=auth_headers(token),
        )
        assert resp.status_code == 200

        # 4. Деактивация SSO-интеграции
        resp = await client.post(
            f"{API}/orgs/{org_id}/sso-integrations/{integration_id}/deactivate",
            headers=auth_headers(token),
        )
        assert resp.status_code == 200

        # 5. Проверка — интеграция деактивирована
        resp = await client.get(
            f"{API}/orgs/{org_id}/sso-integrations",
            headers=auth_headers(token),
        )
        assert resp.status_code == 200
        integrations = resp.json()["data"]
        target = next((i for i in integrations if i["id"] == integration_id), None)
        assert target is not None
        assert target.get("status") == "INACTIVE" or target.get("is_active") is False

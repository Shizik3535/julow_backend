"""E2E-тесты: GET /orgs/{org_id}/sso-integrations."""

import uuid

import pytest

from tests.e2e.conftest import API, auth_headers


@pytest.mark.e2e
class TestGetSSOIntegrations:
    """Список SSO-интеграций."""

    async def test_get_sso_integrations_success(self, client, org_with_owner) -> None:
        """200 — список SSO-интеграций (пустой изначально)."""
        owner = org_with_owner
        resp = await client.get(
            f"{API}/orgs/{owner['org_id']}/sso-integrations",
            headers=auth_headers(owner["access_token"])
        )

        assert resp.status_code == 200
        data = resp.json()["data"]
        assert isinstance(data, list)

    async def test_get_sso_integrations_not_found(self, client, org_with_owner) -> None:
        """404 — организация не найдена."""
        owner = org_with_owner
        resp = await client.get(
            f"{API}/orgs/{uuid.uuid4()}/sso-integrations",
            headers=auth_headers(owner["access_token"])
        )
        assert resp.status_code == 404

    async def test_get_sso_integrations_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.get(f"{API}/orgs/{uuid.uuid4()}/sso-integrations")
        assert resp.status_code == 401

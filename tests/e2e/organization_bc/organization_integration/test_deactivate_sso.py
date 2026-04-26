"""E2E-тесты: POST /orgs/{org_id}/sso-integrations/{integration_id}/deactivate."""

import uuid

import pytest

from tests.e2e.conftest import API, auth_headers, register_and_login


@pytest.mark.e2e
class TestDeactivateSSOIntegration:
    """Деактивация SSO-интеграции."""

    async def _create_sso(self, client, owner) -> str:
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/sso-integrations",
            json={
                "provider": "saml",
                "entity_id": f"https://idp.example.com/{uuid.uuid4().hex[:8]}",
                "sso_url": "https://idp.example.com/sso",
                "certificate": "MIICpDCCAYwCCQDU+jh+",
            },
            headers=auth_headers(owner["access_token"])
        )
        assert resp.status_code == 201
        return resp.json()["data"]["id"]

    async def test_deactivate_sso_integration_success(self, client, org_with_owner) -> None:
        """200 — деактивация SSO-интеграции."""
        owner = org_with_owner
        integration_id = await self._create_sso(client, owner)
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/sso-integrations/{integration_id}/deactivate",
            headers=auth_headers(owner["access_token"])
        )

        assert resp.status_code == 200

    async def test_deactivate_sso_integration_forbidden(self, client, org_with_owner) -> None:
        """403 — не-владелец не может деактивировать SSO."""
        owner = org_with_owner
        integration_id = await self._create_sso(client, owner)
        other = await register_and_login(client)
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/sso-integrations/{integration_id}/deactivate",
            headers=auth_headers(other["access_token"])
        )
        assert resp.status_code == 403

    async def test_deactivate_sso_integration_not_found(self, client, org_with_owner) -> None:
        """404 — интеграция не найдена."""
        owner = org_with_owner
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/sso-integrations/{uuid.uuid4()}/deactivate",
            headers=auth_headers(owner["access_token"])
        )
        assert resp.status_code == 404

    async def test_deactivate_sso_integration_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.post(
            f"{API}/orgs/{uuid.uuid4()}/sso-integrations/{uuid.uuid4()}/deactivate"
        )
        assert resp.status_code == 401

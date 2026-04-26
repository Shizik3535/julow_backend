"""E2E-тесты: PATCH /orgs/{org_id}/sso-integrations/{integration_id}."""

import uuid

import pytest

from tests.e2e.conftest import API, auth_headers, register_and_login


@pytest.mark.e2e
class TestUpdateSSOIntegration:
    """Обновление SSO-интеграции."""

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

    async def test_update_sso_integration_success(self, client, org_with_owner) -> None:
        """200 — обновление параметров SSO."""
        owner = org_with_owner
        integration_id = await self._create_sso(client, owner)
        resp = await client.patch(
            f"{API}/orgs/{owner['org_id']}/sso-integrations/{integration_id}",
            json={"sso_url": "https://new-idp.example.com/sso"},
            headers=auth_headers(owner["access_token"])
        )

        assert resp.status_code == 200

    async def test_update_sso_integration_forbidden(self, client, org_with_owner) -> None:
        """403 — не-владелец не может обновить SSO."""
        owner = org_with_owner
        integration_id = await self._create_sso(client, owner)
        other = await register_and_login(client)
        resp = await client.patch(
            f"{API}/orgs/{owner['org_id']}/sso-integrations/{integration_id}",
            json={"sso_url": "https://hacked.example.com/sso"},
            headers=auth_headers(other["access_token"])
        )
        assert resp.status_code == 403

    async def test_update_sso_integration_not_found(self, client, org_with_owner) -> None:
        """404 — интеграция не найдена."""
        owner = org_with_owner
        resp = await client.patch(
            f"{API}/orgs/{owner['org_id']}/sso-integrations/{uuid.uuid4()}",
            json={"sso_url": "https://ghost.example.com/sso"},
            headers=auth_headers(owner["access_token"])
        )
        assert resp.status_code == 404

    async def test_update_sso_integration_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.patch(
            f"{API}/orgs/{uuid.uuid4()}/sso-integrations/{uuid.uuid4()}",
            json={"sso_url": "https://noauth.example.com/sso"}
        )
        assert resp.status_code == 401

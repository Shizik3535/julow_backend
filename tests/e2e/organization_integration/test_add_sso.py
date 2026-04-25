"""E2E-тесты: POST /orgs/{org_id}/sso-integrations."""

import uuid

import pytest

from tests.e2e.conftest import API, auth_headers, create_org_with_owner, register_and_login


@pytest.mark.e2e
class TestAddSSOIntegration:
    """Добавление SSO-интеграции."""

    async def test_add_sso_integration_success(self, client) -> None:
        """201 — добавление SSO-интеграции (SAML)."""
        owner = await create_org_with_owner(client)
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/sso-integrations",
            json={
                "provider": "saml",
                "entity_id": f"https://idp.example.com/{uuid.uuid4().hex[:8]}",
                "sso_url": "https://idp.example.com/sso",
                "certificate": "MIICpDCCAYwCCQDU+jh+",
            },
            headers=auth_headers(owner["access_token"]),
        )

        assert resp.status_code == 201
        data = resp.json()["data"]
        assert data["id"]

    async def test_add_sso_integration_forbidden(self, client) -> None:
        """403 — не-владелец не может добавить SSO."""
        owner = await create_org_with_owner(client)
        other = await register_and_login(client)
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/sso-integrations",
            json={
                "provider": "saml",
                "entity_id": "https://idp.example.com/hack",
                "sso_url": "https://idp.example.com/sso",
                "certificate": "MIICpDCCAYwCCQDU",
            },
            headers=auth_headers(other["access_token"]),
        )
        assert resp.status_code == 403

    async def test_add_sso_integration_not_found(self, client) -> None:
        """404 — организация не найдена."""
        owner = await create_org_with_owner(client)
        resp = await client.post(
            f"{API}/orgs/{uuid.uuid4()}/sso-integrations",
            json={
                "provider": "saml",
                "entity_id": "https://idp.example.com/ghost",
                "sso_url": "https://idp.example.com/sso",
                "certificate": "MIICpDCCAYwCCQDU",
            },
            headers=auth_headers(owner["access_token"]),
        )
        assert resp.status_code == 404

    async def test_add_sso_integration_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.post(
            f"{API}/orgs/{uuid.uuid4()}/sso-integrations",
            json={
                "provider": "saml",
                "entity_id": "https://idp.example.com/noauth",
                "sso_url": "https://idp.example.com/sso",
                "certificate": "MIICpDCCAYwCCQDU",
            },
        )
        assert resp.status_code == 401

    async def test_add_sso_integration_validation(self, client) -> None:
        """422 — отсутствуют обязательные поля."""
        owner = await create_org_with_owner(client)
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/sso-integrations",
            json={"provider": "saml"},
            headers=auth_headers(owner["access_token"]),
        )
        assert resp.status_code == 422

"""E2E-тесты: POST /orgs/{org_id}/reactivate."""

import uuid

import pytest

from tests.e2e.conftest import API, auth_headers, create_org_with_owner, register_and_login


@pytest.mark.e2e
class TestReactivateOrganization:
    """Реактивация организации."""

    async def test_reactivate_organization_success(self, client) -> None:
        """200 — реактивация приостановленной организации."""
        owner = await create_org_with_owner(client)
        await client.post(
            f"{API}/orgs/{owner['org_id']}/suspend",
            json={"reason": "Temp"},
            headers=auth_headers(owner["access_token"]),
        )
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/reactivate",
            headers=auth_headers(owner["access_token"]),
        )

        assert resp.status_code == 200

    async def test_reactivate_organization_already_active(self, client) -> None:
        """409 — реактивация активной организации."""
        owner = await create_org_with_owner(client)
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/reactivate",
            headers=auth_headers(owner["access_token"]),
        )
        assert resp.status_code == 409

    async def test_reactivate_organization_forbidden(self, client) -> None:
        """403 — не-владелец не может реактивировать."""
        owner = await create_org_with_owner(client)
        other = await register_and_login(client)
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/reactivate",
            headers=auth_headers(other["access_token"]),
        )
        assert resp.status_code == 403

    async def test_reactivate_organization_not_found(self, client) -> None:
        """404 — организация не найдена."""
        owner = await create_org_with_owner(client)
        resp = await client.post(
            f"{API}/orgs/{uuid.uuid4()}/reactivate",
            headers=auth_headers(owner["access_token"]),
        )
        assert resp.status_code == 404

    async def test_reactivate_organization_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.post(f"{API}/orgs/{uuid.uuid4()}/reactivate")
        assert resp.status_code == 401

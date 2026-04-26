"""E2E-тесты: POST /orgs/{org_id}/suspend."""

import uuid

import pytest

from tests.e2e.conftest import API, auth_headers, register_and_login


@pytest.mark.e2e
class TestSuspendOrganization:
    """Приостановка организации."""
    async def test_suspend_organization_already_suspended(self, client, org_with_owner) -> None:
        """409 — повторная приостановка уже приостановленной организации."""
        owner = org_with_owner
        await client.post(
            f"{API}/orgs/{owner['org_id']}/suspend",
            json={"reason": "First"},
            headers=auth_headers(owner["access_token"])
        )
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/suspend",
            json={"reason": "Second"},
            headers=auth_headers(owner["access_token"])
        )
        assert resp.status_code == 409
    async def test_suspend_organization_forbidden(self, client, org_with_owner) -> None:
        """403 — не-владелец не может приостановить."""
        owner = org_with_owner
        other = await register_and_login(client)
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/suspend",
            json={"reason": "Hack"},
            headers=auth_headers(other["access_token"])
        )
        assert resp.status_code == 403
    async def test_suspend_organization_not_found(self, client, org_with_owner) -> None:
        """404 — организация не найдена."""
        owner = org_with_owner
        resp = await client.post(
            f"{API}/orgs/{uuid.uuid4()}/suspend",
            json={"reason": "Ghost"},
            headers=auth_headers(owner["access_token"])
        )
        assert resp.status_code == 404
    async def test_suspend_organization_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.post(
            f"{API}/orgs/{uuid.uuid4()}/suspend",
            json={"reason": "NoAuth"}
        )
        assert resp.status_code == 401
    async def test_suspend_organization_success(self, client, org_with_owner) -> None:
        """200 — владелец приостанавливает организацию."""
        owner = org_with_owner
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/suspend",
            json={"reason": "Maintenance"},
            headers=auth_headers(owner["access_token"])
        )

        assert resp.status_code == 200

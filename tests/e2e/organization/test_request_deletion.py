"""E2E-тесты: POST /orgs/{org_id}/request-deletion."""

import uuid

import pytest

from tests.e2e.conftest import API, auth_headers, create_org_with_owner, register_and_login


@pytest.mark.e2e
class TestRequestOrganizationDeletion:
    """Запрос удаления организации."""

    async def test_request_deletion_success(self, client) -> None:
        """200 — владелец запрашивает удаление."""
        owner = await create_org_with_owner(client)
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/request-deletion",
            headers=auth_headers(owner["access_token"]),
        )

        assert resp.status_code == 200

    async def test_request_deletion_already_requested(self, client) -> None:
        """409 — повторный запрос удаления."""
        owner = await create_org_with_owner(client)
        await client.post(
            f"{API}/orgs/{owner['org_id']}/request-deletion",
            headers=auth_headers(owner["access_token"]),
        )
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/request-deletion",
            headers=auth_headers(owner["access_token"]),
        )
        assert resp.status_code == 409

    async def test_request_deletion_forbidden(self, client) -> None:
        """403 — не-владелец не может запросить удаление."""
        owner = await create_org_with_owner(client)
        other = await register_and_login(client)
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/request-deletion",
            headers=auth_headers(other["access_token"]),
        )
        assert resp.status_code == 403

    async def test_request_deletion_not_found(self, client) -> None:
        """404 — организация не найдена."""
        owner = await create_org_with_owner(client)
        resp = await client.post(
            f"{API}/orgs/{uuid.uuid4()}/request-deletion",
            headers=auth_headers(owner["access_token"]),
        )
        assert resp.status_code == 404

    async def test_request_deletion_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.post(f"{API}/orgs/{uuid.uuid4()}/request-deletion")
        assert resp.status_code == 401

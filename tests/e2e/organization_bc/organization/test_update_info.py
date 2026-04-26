"""E2E-тесты: PATCH /orgs/{org_id}."""

import uuid

import pytest

from tests.e2e.conftest import API, auth_headers, register_and_login


@pytest.mark.e2e
class TestUpdateOrganizationInfo:
    """Обновление информации организации."""

    async def test_update_organization_info_success(self, client, org_with_owner) -> None:
        """200 — владелец обновляет информацию."""
        owner = org_with_owner
        resp = await client.patch(
            f"{API}/orgs/{owner['org_id']}",
            json={"name": "Updated Org Name"},
            headers=auth_headers(owner["access_token"])
        )

        assert resp.status_code == 200

    async def test_update_organization_info_forbidden(self, client, org_with_owner) -> None:
        """403 — не-владелец не может обновить информацию."""
        owner = org_with_owner
        other = await register_and_login(client)
        resp = await client.patch(
            f"{API}/orgs/{owner['org_id']}",
            json={"name": "Hacked Name"},
            headers=auth_headers(other["access_token"])
        )
        assert resp.status_code == 403

    async def test_update_organization_info_not_found(self, client, org_with_owner) -> None:
        """404 — организация не найдена."""
        owner = org_with_owner
        resp = await client.patch(
            f"{API}/orgs/{uuid.uuid4()}",
            json={"name": "Ghost Org"},
            headers=auth_headers(owner["access_token"])
        )
        assert resp.status_code == 404

    async def test_update_organization_info_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.patch(
            f"{API}/orgs/{uuid.uuid4()}",
            json={"name": "NoAuth Org"}
        )
        assert resp.status_code == 401

    async def test_update_organization_info_validation(self, client, org_with_owner) -> None:
        """422 — пустое название."""
        owner = org_with_owner
        resp = await client.patch(
            f"{API}/orgs/{owner['org_id']}",
            json={"name": ""},
            headers=auth_headers(owner["access_token"])
        )
        assert resp.status_code == 422

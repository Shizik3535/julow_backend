"""E2E-тесты: PATCH /orgs/{org_id}/membership-policy."""

import uuid

import pytest

from tests.e2e.conftest import API, auth_headers, create_org_with_owner, register_and_login


@pytest.mark.e2e
class TestUpdateMembershipPolicy:
    """Обновление политики членства."""

    async def test_update_membership_policy_success(self, client) -> None:
        """200 — владелец обновляет политику членства."""
        owner = await create_org_with_owner(client)
        resp = await client.patch(
            f"{API}/orgs/{owner['org_id']}/membership-policy",
            json={"max_members": 50, "require_approval": True},
            headers=auth_headers(owner["access_token"]),
        )

        assert resp.status_code == 200

    async def test_update_membership_policy_forbidden(self, client) -> None:
        """403 — не-владелец не может обновить политику."""
        owner = await create_org_with_owner(client)
        other = await register_and_login(client)
        resp = await client.patch(
            f"{API}/orgs/{owner['org_id']}/membership-policy",
            json={"max_members": 100},
            headers=auth_headers(other["access_token"]),
        )
        assert resp.status_code == 403

    async def test_update_membership_policy_not_found(self, client) -> None:
        """404 — организация не найдена."""
        owner = await create_org_with_owner(client)
        resp = await client.patch(
            f"{API}/orgs/{uuid.uuid4()}/membership-policy",
            json={"max_members": 100},
            headers=auth_headers(owner["access_token"]),
        )
        assert resp.status_code == 404

    async def test_update_membership_policy_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.patch(
            f"{API}/orgs/{uuid.uuid4()}/membership-policy",
            json={"max_members": 100},
        )
        assert resp.status_code == 401

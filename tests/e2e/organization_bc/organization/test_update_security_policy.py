"""E2E-тесты: PATCH /orgs/{org_id}/security-policy."""

import uuid

import pytest

from tests.e2e.conftest import API, auth_headers, register_and_login


@pytest.mark.e2e
class TestUpdateSecurityPolicy:
    """Обновление политики безопасности."""

    async def test_update_security_policy_success(self, client, org_with_owner) -> None:
        """200 — владелец обновляет политику безопасности."""
        owner = org_with_owner
        resp = await client.patch(
            f"{API}/orgs/{owner['org_id']}/security-policy",
            json={"require_2fa": True, "password_min_length": 12},
            headers=auth_headers(owner["access_token"])
        )

        assert resp.status_code == 200

    async def test_update_security_policy_forbidden(self, client, org_with_owner) -> None:
        """403 — не-владелец не может обновить политику."""
        owner = org_with_owner
        other = await register_and_login(client)
        resp = await client.patch(
            f"{API}/orgs/{owner['org_id']}/security-policy",
            json={"require_2fa": True},
            headers=auth_headers(other["access_token"])
        )
        assert resp.status_code == 403

    async def test_update_security_policy_not_found(self, client, org_with_owner) -> None:
        """404 — организация не найдена."""
        owner = org_with_owner
        resp = await client.patch(
            f"{API}/orgs/{uuid.uuid4()}/security-policy",
            json={"require_2fa": True},
            headers=auth_headers(owner["access_token"])
        )
        assert resp.status_code == 404

    async def test_update_security_policy_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.patch(
            f"{API}/orgs/{uuid.uuid4()}/security-policy",
            json={"require_2fa": True}
        )
        assert resp.status_code == 401

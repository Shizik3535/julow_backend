"""E2E-тесты: PATCH /orgs/{org_id}/security-policy."""

import uuid

import pytest

from tests.e2e.conftest import API, auth_headers, create_org_with_owner, register_and_login


@pytest.mark.e2e
class TestUpdateSecurityPolicy:
    """Обновление политики безопасности."""

    async def test_update_security_policy_success(self, client) -> None:
        """200 — владелец обновляет политику безопасности."""
        owner = await create_org_with_owner(client)
        resp = await client.patch(
            f"{API}/orgs/{owner['org_id']}/security-policy",
            json={"require_2fa": True, "password_min_length": 12},
            headers=auth_headers(owner["access_token"]),
        )

        assert resp.status_code == 200

    async def test_update_security_policy_forbidden(self, client) -> None:
        """403 — не-владелец не может обновить политику."""
        owner = await create_org_with_owner(client)
        other = await register_and_login(client)
        resp = await client.patch(
            f"{API}/orgs/{owner['org_id']}/security-policy",
            json={"require_2fa": True},
            headers=auth_headers(other["access_token"]),
        )
        assert resp.status_code == 403

    async def test_update_security_policy_not_found(self, client) -> None:
        """404 — организация не найдена."""
        owner = await create_org_with_owner(client)
        resp = await client.patch(
            f"{API}/orgs/{uuid.uuid4()}/security-policy",
            json={"require_2fa": True},
            headers=auth_headers(owner["access_token"]),
        )
        assert resp.status_code == 404

    async def test_update_security_policy_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.patch(
            f"{API}/orgs/{uuid.uuid4()}/security-policy",
            json={"require_2fa": True},
        )
        assert resp.status_code == 401

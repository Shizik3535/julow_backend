"""E2E-тесты: DELETE /account/security/oauth/{provider}."""

import pytest

from tests.e2e.conftest import API, auth_headers, register_and_login


@pytest.mark.e2e
class TestUnlinkOAuth:
    """Отвязка OAuth-провайдера."""

    async def test_unlink_oauth_success(self, client) -> None:
        """200 — OAuth-провайдер отвязан (после предварительной привязки)."""
        user = await register_and_login(client)
        headers = auth_headers(user["access_token"])

        # Привязываем
        link_resp = await client.post(
            f"{API}/account/security/oauth/link",
            json={
                "provider": "oauth_google",
                "authorization_code": "test-auth-code-12345",
                "redirect_uri": "https://app.example.com/oauth/callback",
            },
            headers=headers,
        )
        assert link_resp.status_code == 200

        # Отвязываем
        resp = await client.delete(
            f"{API}/account/security/oauth/oauth_google",
            headers=headers,
        )
        assert resp.status_code == 200

    async def test_unlink_oauth_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.delete(
            f"{API}/account/security/oauth/oauth_google"
        )
        assert resp.status_code == 401

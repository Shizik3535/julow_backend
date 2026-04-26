"""E2E-тесты: POST /account/security/oauth/link."""

import pytest

from tests.e2e.conftest import API


@pytest.mark.e2e
class TestLinkOAuth:
    """Привязка OAuth-провайдера."""

    async def test_link_oauth_success(self, auth_client) -> None:
        """200 — OAuth-провайдер привязан."""
        resp = await auth_client.post(
            f"{API}/account/security/oauth/link",
            json={
                "provider": "oauth_google",
                "authorization_code": "test-auth-code-12345",
                "redirect_uri": "https://app.example.com/oauth/callback",
            }
        )
        assert resp.status_code == 200

    async def test_link_oauth_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.post(
            f"{API}/account/security/oauth/link",
            json={
                "provider": "oauth_google",
                "authorization_code": "test-auth-code",
                "redirect_uri": "https://app.example.com/oauth/callback",
            }
        )
        assert resp.status_code == 401

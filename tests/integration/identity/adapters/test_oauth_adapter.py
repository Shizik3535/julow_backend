"""Интеграционные тесты HttpxOAuthAdapter (mock HTTP через respx)."""

import pytest
import respx
from httpx import Response

from app.context.identity.infrastructure.oauth.oauth_adapter import HttpxOAuthAdapter


@pytest.mark.integration
class TestHttpxOAuthAdapter:
    """Тесты OAuth через httpx + мокнутые HTTP-ответы (respx)."""

    @pytest.fixture
    def adapter(self) -> HttpxOAuthAdapter:
        return HttpxOAuthAdapter(
            client_id_map={"oauth_google": "google-client-id", "oauth_github": "github-client-id"},
            client_secret_map={"oauth_google": "google-secret", "oauth_github": "github-secret"},
        )

    # ── Google ────────────────────────────────────────────────────────────

    @respx.mock
    async def test_exchange_code_google(self, adapter: HttpxOAuthAdapter) -> None:
        respx.post("https://oauth2.googleapis.com/token").mock(
            return_value=Response(200, json={"access_token": "google-access-123"})
        )
        token = await adapter.exchange_code("oauth_google", "auth-code", "http://localhost/callback")
        assert token == "google-access-123"

    @respx.mock
    async def test_get_user_info_google(self, adapter: HttpxOAuthAdapter) -> None:
        respx.get("https://www.googleapis.com/oauth2/v3/userinfo").mock(
            return_value=Response(200, json={
                "sub": "google-user-id-123",
                "email": "user@gmail.com",
                "name": "Google User",
            })
        )
        info = await adapter.get_user_info("oauth_google", "access-token")
        assert info.provider_user_id == "google-user-id-123"
        assert info.email == "user@gmail.com"
        assert info.display_name == "Google User"

    # ── GitHub ────────────────────────────────────────────────────────────

    @respx.mock
    async def test_exchange_code_github(self, adapter: HttpxOAuthAdapter) -> None:
        respx.post("https://github.com/login/oauth/access_token").mock(
            return_value=Response(200, json={"access_token": "github-access-456"})
        )
        token = await adapter.exchange_code("oauth_github", "auth-code", "http://localhost/callback")
        assert token == "github-access-456"

    @respx.mock
    async def test_get_user_info_github(self, adapter: HttpxOAuthAdapter) -> None:
        respx.get("https://api.github.com/user").mock(
            return_value=Response(200, json={
                "id": 12345,
                "email": "user@github.com",
                "login": "github-user",
            })
        )
        info = await adapter.get_user_info("oauth_github", "access-token")
        assert info.provider_user_id == "12345"
        assert info.email == "user@github.com"
        assert info.display_name == "github-user"

    # ── Error cases ───────────────────────────────────────────────────────

    @respx.mock
    async def test_exchange_code_no_access_token_raises(self, adapter: HttpxOAuthAdapter) -> None:
        respx.post("https://oauth2.googleapis.com/token").mock(
            return_value=Response(200, json={"error": "invalid_grant"})
        )
        with pytest.raises(RuntimeError, match="access_token"):
            await adapter.exchange_code("oauth_google", "bad-code", "http://localhost/callback")

    def test_unknown_provider_raises(self, adapter: HttpxOAuthAdapter) -> None:
        with pytest.raises(ValueError, match="Неизвестный"):
            adapter._get_config("oauth_unknown")

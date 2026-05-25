from unittest.mock import AsyncMock, MagicMock

import pytest

from app.context.identity.application.commands.login_oauth import (
    LoginOAuthCommand,
    LoginOAuthHandler,
)
from app.context.identity.application.ports.oauth.oauth_port import OAuthUserInfo
from app.context.identity.domain.value_objects.auth_provider import AuthProvider
from app.shared.application.ports.auth.auth_dto import TokenPair


@pytest.mark.integration
class TestLoginOAuthHandler:
    @pytest.mark.asyncio
    async def test_auto_register_uses_valid_fallback_email_when_provider_email_is_missing(self):
        user_repo = AsyncMock()
        user_auth_repo = AsyncMock()
        user_auth_repo.get_by_oauth_provider = AsyncMock(return_value=None)
        user_auth_repo.get_by_email = AsyncMock(return_value=None)
        session_repo = AsyncMock()
        role_repo = AsyncMock()
        role_repo.get_by_name = AsyncMock(return_value=None)
        oauth_port = AsyncMock()
        oauth_port.exchange_code = AsyncMock(return_value="oauth-access-token")
        oauth_port.get_user_info = AsyncMock(
            return_value=OAuthUserInfo(
                provider_user_id="152811563",
                email=None,
                display_name="github-user",
            )
        )
        auth_token_port = MagicMock()
        auth_token_port.generate_token_pair = MagicMock(
            return_value=TokenPair(
                access_token="access-token",
                refresh_token="refresh-token",
                access_expires_in=3600,
                refresh_expires_in=604800,
            )
        )
        failed_login_policy = MagicMock()
        event_bus = AsyncMock()
        event_bus.publish_all = AsyncMock(return_value=None)

        handler = LoginOAuthHandler(
            user_repo=user_repo,
            user_auth_repo=user_auth_repo,
            session_repo=session_repo,
            role_repo=role_repo,
            oauth_port=oauth_port,
            auth_token_port=auth_token_port,
            failed_login_policy=failed_login_policy,
            event_bus=event_bus,
        )
        command = LoginOAuthCommand(
            provider=AuthProvider.OAUTH_GITHUB.value,
            authorization_code="oauth-code",
            redirect_uri="https://julow.ru/oauth/callback",
            ip="127.0.0.1",
            user_agent="pytest",
        )

        result = await handler.handle(command)

        assert result.user.email == "152811563@oauth-github.invalid"
        user_repo.add.assert_awaited_once()
        user_auth_repo.add.assert_awaited_once()
        session_repo.add.assert_awaited_once()

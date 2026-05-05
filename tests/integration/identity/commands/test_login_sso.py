"""Интеграционные-тесты для SSO-логина (initiate + callback + enforce_sso)."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.context.identity.application.commands.initiate_sso_login import (
    InitiateSSOLoginCommand,
    InitiateSSOLoginHandler,
)
from app.context.identity.application.commands.login_user import (
    LoginUserCommand,
    LoginUserHandler,
)
from app.context.identity.application.dto.sso_config_dto import SSOConfigDTO
from app.context.identity.application.exceptions.auth_app_exceptions import SSOEnforcedException
from app.context.identity.infrastructure.sso.exceptions import SSOAuthenticationException


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def mock_org_sso_port():
    port = AsyncMock()
    port.get_sso_config_by_email_domain = AsyncMock(return_value=None)
    port.is_sso_enforced = AsyncMock(return_value=False)
    return port


@pytest.fixture()
def mock_sso_port():
    port = MagicMock()
    port.supports_protocol = MagicMock(return_value=True)
    port.build_auth_request = MagicMock(return_value="https://idp.example.com/sso?SAMLRequest=xxx")
    return port


@pytest.fixture()
def sso_config():
    return SSOConfigDTO(
        org_id="00000000-0000-0000-0000-000000000001",
        provider="saml",
        entity_id="https://idp.example.com",
        sso_url="https://idp.example.com/sso",
        certificate="CERT",
        enforce_sso=True,
        auto_provision=True,
        default_role_id="00000000-0000-0000-0000-000000000099",
        email_domains=["company.com"],
    )


# ---------------------------------------------------------------------------
# InitiateSSOLoginHandler
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestInitiateSSOLoginHandler:
    """Тесты инициации SSO-логина."""

    @pytest.mark.asyncio
    async def test_initiate_sso_login_returns_redirect_url(
        self, mock_org_sso_port, mock_sso_port, sso_config,
    ):
        mock_org_sso_port.get_sso_config_by_email_domain.return_value = sso_config

        handler = InitiateSSOLoginHandler(
            org_sso_port=mock_org_sso_port,
            sso_port=mock_sso_port,
        )
        command = InitiateSSOLoginCommand(
            email="user@company.com",
            callback_url="https://app.example.com/auth/login/sso/callback",
        )
        result = await handler.handle(command)
        assert result.redirect_url == "https://idp.example.com/sso?SAMLRequest=xxx"
        mock_org_sso_port.get_sso_config_by_email_domain.assert_awaited_once_with("company.com")

    @pytest.mark.asyncio
    async def test_initiate_sso_login_raises_when_no_config(
        self, mock_org_sso_port, mock_sso_port,
    ):
        mock_org_sso_port.get_sso_config_by_email_domain.return_value = None

        handler = InitiateSSOLoginHandler(
            org_sso_port=mock_org_sso_port,
            sso_port=mock_sso_port,
        )
        command = InitiateSSOLoginCommand(
            email="user@unknown.com",
            callback_url="https://app.example.com/auth/login/sso/callback",
        )
        with pytest.raises(SSOAuthenticationException):
            await handler.handle(command)

    @pytest.mark.asyncio
    async def test_initiate_sso_login_raises_when_unsupported_protocol(
        self, mock_org_sso_port, mock_sso_port, sso_config,
    ):
        mock_org_sso_port.get_sso_config_by_email_domain.return_value = sso_config
        mock_sso_port.supports_protocol.return_value = False

        handler = InitiateSSOLoginHandler(
            org_sso_port=mock_org_sso_port,
            sso_port=mock_sso_port,
        )
        command = InitiateSSOLoginCommand(
            email="user@company.com",
            callback_url="https://app.example.com/auth/login/sso/callback",
        )
        with pytest.raises(SSOAuthenticationException):
            await handler.handle(command)


# ---------------------------------------------------------------------------
# enforce_sso в LoginUserHandler
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestEnforceSSO:
    """Тесты блокировки обычного логина при enforce_sso."""

    @pytest.mark.asyncio
    async def test_login_blocked_when_sso_enforced(self, mock_org_sso_port):
        mock_org_sso_port.is_sso_enforced.return_value = True

        handler = LoginUserHandler(
            user_repo=AsyncMock(),
            user_auth_repo=AsyncMock(),
            session_repo=AsyncMock(),
            password_port=MagicMock(),
            auth_token_port=MagicMock(),
            failed_login_policy=MagicMock(),
            event_bus=AsyncMock(),
            org_sso_port=mock_org_sso_port,
        )
        command = LoginUserCommand(
            email="user@company.com",
            password="password123",
        )
        with pytest.raises(SSOEnforcedException):
            await handler.handle(command)

    @pytest.mark.asyncio
    async def test_login_allowed_when_sso_not_enforced(self, mock_org_sso_port):
        """Если enforce_sso=false, логин проходит дальше (в AuthenticationFailedException из-за mock)."""
        from app.context.identity.application.exceptions.auth_app_exceptions import AuthenticationFailedException

        mock_org_sso_port.is_sso_enforced.return_value = False

        user_auth_repo = AsyncMock()
        user_auth_repo.get_by_email = AsyncMock(return_value=None)

        handler = LoginUserHandler(
            user_repo=AsyncMock(),
            user_auth_repo=user_auth_repo,
            session_repo=AsyncMock(),
            password_port=MagicMock(),
            auth_token_port=MagicMock(),
            failed_login_policy=MagicMock(),
            event_bus=AsyncMock(),
            org_sso_port=mock_org_sso_port,
        )
        command = LoginUserCommand(
            email="user@company.com",
            password="password123",
        )
        # Должен дойти до проверки credentials, а не упасть на SSO
        with pytest.raises(AuthenticationFailedException):
            await handler.handle(command)

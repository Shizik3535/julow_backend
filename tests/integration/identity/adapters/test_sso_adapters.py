"""Интеграционные-тесты для SSO-адаптеров (Composite, SAML, OIDC, LDAP)."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.context.identity.application.ports.sso.sso_port import SSOUserInfo
from app.context.identity.infrastructure.sso.composite_sso_adapter import CompositeSSOAdapter
from app.context.identity.infrastructure.sso.exceptions import SSOAuthenticationException


@pytest.mark.integration
class TestCompositeSSOAdapter:
    """Тесты CompositeSSOAdapter."""

    def _make_adapter(self, protocol: str) -> MagicMock:
        adapter = MagicMock()
        adapter.supports_protocol = MagicMock(side_effect=lambda p: p == protocol)
        adapter.build_auth_request = MagicMock(return_value=f"https://{protocol}.example.com/auth")
        adapter.process_response = AsyncMock(
            return_value=SSOUserInfo(
                provider_user_id="uid-1",
                email=f"user@{protocol}.example.com",
            )
        )
        return adapter

    def test_supports_protocol_delegates(self):
        saml = self._make_adapter("saml")
        oidc = self._make_adapter("oidc")
        composite = CompositeSSOAdapter(adapters=[saml, oidc])

        assert composite.supports_protocol("saml") is True
        assert composite.supports_protocol("oidc") is True
        assert composite.supports_protocol("ldap") is False

    def test_build_auth_request_delegates_to_correct_adapter(self):
        saml = self._make_adapter("saml")
        oidc = self._make_adapter("oidc")
        composite = CompositeSSOAdapter(adapters=[saml, oidc])

        result = composite.build_auth_request(
            provider="saml",
            entity_id="entity",
            sso_url="https://idp.example.com",
            certificate="CERT",
            callback_url="https://app.example.com/callback",
        )
        assert result == "https://saml.example.com/auth"
        saml.build_auth_request.assert_called_once()
        oidc.build_auth_request.assert_not_called()

    def test_build_auth_request_raises_for_unsupported(self):
        saml = self._make_adapter("saml")
        composite = CompositeSSOAdapter(adapters=[saml])

        with pytest.raises(SSOAuthenticationException, match="Unsupported SSO provider"):
            composite.build_auth_request(
                provider="ldap",
                entity_id="entity",
                sso_url="url",
                certificate="cert",
                callback_url="cb",
            )

    @pytest.mark.asyncio
    async def test_process_response_delegates_to_correct_adapter(self):
        saml = self._make_adapter("saml")
        oidc = self._make_adapter("oidc")
        composite = CompositeSSOAdapter(adapters=[saml, oidc])

        result = await composite.process_response(
            provider="oidc",
            entity_id="entity",
            sso_url="https://idp.example.com",
            certificate="CERT",
            callback_url="https://app.example.com/callback",
            response_data={"code": "abc"},
        )
        assert result.email == "user@oidc.example.com"
        oidc.process_response.assert_awaited_once()
        saml.process_response.assert_not_awaited()

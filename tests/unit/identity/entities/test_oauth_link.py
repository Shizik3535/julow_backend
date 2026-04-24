"""Unit-тесты для OAuthLink."""

from datetime import datetime

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.identity.domain.entities.oauth_link import OAuthLink
from app.context.identity.domain.value_objects.auth_provider import AuthProvider


@pytest.mark.unit
class TestOAuthLink:
    def test_create_oauth_link(self) -> None:
        link = OAuthLink(provider=AuthProvider.OAUTH_GOOGLE, provider_user_id="google_123")
        assert link.provider == AuthProvider.OAUTH_GOOGLE
        assert link.provider_user_id == "google_123"
        assert isinstance(link.id, Id)
        assert isinstance(link.linked_at, datetime)

    def test_create_saml_link(self) -> None:
        link = OAuthLink(provider=AuthProvider.SAML_SSO, provider_user_id="saml_user")
        assert link.provider == AuthProvider.SAML_SSO

    def test_equality_by_id(self) -> None:
        shared_id = Id.generate()
        link1 = OAuthLink(id=shared_id, provider=AuthProvider.OAUTH_GOOGLE, provider_user_id="123")
        link2 = OAuthLink(id=shared_id, provider=AuthProvider.OAUTH_GOOGLE, provider_user_id="123")
        assert link1 == link2

    def test_inequality_different_id(self) -> None:
        link1 = OAuthLink(provider=AuthProvider.OAUTH_GOOGLE, provider_user_id="123")
        link2 = OAuthLink(provider=AuthProvider.OAUTH_GOOGLE, provider_user_id="123")
        assert link1 != link2

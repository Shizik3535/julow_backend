"""Unit-тесты для AuthProvider."""

import pytest

from app.context.identity.domain.value_objects.auth_provider import AuthProvider


@pytest.mark.unit
class TestAuthProvider:
    def test_all_providers_exist(self) -> None:
        assert AuthProvider.EMAIL_PASSWORD.value == "email_password"
        assert AuthProvider.OAUTH_GOOGLE.value == "oauth_google"
        assert AuthProvider.OAUTH_GITHUB.value == "oauth_github"
        assert AuthProvider.OAUTH_YANDEX.value == "oauth_yandex"
        assert AuthProvider.OAUTH_APPLE.value == "oauth_apple"
        assert AuthProvider.SAML_SSO.value == "saml_sso"

    def test_providers_are_distinct(self) -> None:
        values = [p.value for p in AuthProvider]
        assert len(values) == len(set(values))

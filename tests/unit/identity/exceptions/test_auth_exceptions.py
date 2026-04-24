"""Unit-тесты для исключений UserAuth aggregate (Identity BC)."""

import pytest

from app.shared.domain.base_exceptions import DomainException
from app.shared.domain.exceptions import BusinessRuleViolationException
from app.context.identity.domain.exceptions.auth_exceptions import (
    InvalidTwoFACodeException,
    OAuthProviderAlreadyLinkedException,
    TwoFARequiredException,
)


@pytest.mark.unit
class TestTwoFARequiredException:
    def test_is_domain(self) -> None:
        exc = TwoFARequiredException()
        assert isinstance(exc, DomainException)


@pytest.mark.unit
class TestInvalidTwoFACodeException:
    def test_is_domain(self) -> None:
        exc = InvalidTwoFACodeException()
        assert isinstance(exc, DomainException)


@pytest.mark.unit
class TestOAuthProviderAlreadyLinkedException:
    def test_is_business_rule(self) -> None:
        exc = OAuthProviderAlreadyLinkedException("google")
        assert isinstance(exc, BusinessRuleViolationException)
        assert exc.provider == "google"

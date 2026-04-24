"""Unit-тесты для SecurityPolicy (Organization BC)."""

import pytest

from app.shared.domain.exceptions import ValidationException
from app.context.organization.domain.value_objects.security_policy import SecurityPolicy


@pytest.mark.unit
class TestSecurityPolicy:
    def test_defaults(self) -> None:
        policy = SecurityPolicy()
        assert policy.require_2fa is False
        assert policy.password_min_length == 8
        assert policy.session_timeout_minutes is None
        assert policy.ip_allowlist == []
        assert policy.domain_restrictions == []
        assert policy.require_email_verification is False

    def test_custom_values(self) -> None:
        policy = SecurityPolicy(
            require_2fa=True,
            password_min_length=12,
            session_timeout_minutes=30,
            ip_allowlist=["10.0.0.0/8"],
            domain_restrictions=["corp.com"],
            require_email_verification=True,
        )
        assert policy.require_2fa is True
        assert policy.password_min_length == 12
        assert policy.session_timeout_minutes == 30

    def test_password_min_length_less_than_8_raises(self) -> None:
        with pytest.raises(ValidationException) as exc_info:
            SecurityPolicy(password_min_length=7)
        assert exc_info.value.field == "password_min_length"

    def test_session_timeout_less_than_one_raises(self) -> None:
        with pytest.raises(ValidationException) as exc_info:
            SecurityPolicy(session_timeout_minutes=0)
        assert exc_info.value.field == "session_timeout_minutes"

    def test_frozen(self) -> None:
        policy = SecurityPolicy()
        with pytest.raises(AttributeError):
            policy.require_2fa = True  # type: ignore[misc]

    def test_equality_by_value(self) -> None:
        assert SecurityPolicy() == SecurityPolicy()

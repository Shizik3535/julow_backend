"""Unit-тесты для SecurityPolicy (Workspace BC)."""

import pytest

from app.shared.domain.exceptions import ValidationException
from app.context.workspace.domain.value_objects.security_policy import SecurityPolicy
from app.context.workspace.domain.value_objects.sso_mode import SSOMode


@pytest.mark.unit
class TestSecurityPolicy:
    def test_defaults(self) -> None:
        policy = SecurityPolicy()
        assert policy.pin_code_enabled is False
        assert policy.password_enabled is True
        assert policy.ip_allowlist == []
        assert policy.sso_mode == SSOMode.NONE
        assert policy.require_2fa is False
        assert policy.session_timeout_minutes is None
        assert policy.inherit_from_parent is False

    def test_custom_values(self) -> None:
        policy = SecurityPolicy(
            pin_code_enabled=True,
            sso_mode=SSOMode.REQUIRED,
            require_2fa=True,
            session_timeout_minutes=30,
        )
        assert policy.pin_code_enabled is True
        assert policy.sso_mode == SSOMode.REQUIRED
        assert policy.session_timeout_minutes == 30

    def test_session_timeout_less_than_1_raises(self) -> None:
        with pytest.raises(ValidationException) as exc_info:
            SecurityPolicy(session_timeout_minutes=0)
        assert exc_info.value.field == "session_timeout_minutes"

    def test_frozen(self) -> None:
        policy = SecurityPolicy()
        with pytest.raises(AttributeError):
            policy.password_enabled = False  # type: ignore[misc]

    def test_equality_by_value(self) -> None:
        assert SecurityPolicy() == SecurityPolicy()

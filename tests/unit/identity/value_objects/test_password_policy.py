"""Unit-тесты для PasswordPolicy."""

import pytest

from app.shared.domain.exceptions import ValidationException
from app.context.identity.domain.value_objects.password_policy import PasswordPolicy


@pytest.mark.unit
class TestPasswordPolicy:
    def test_default_policy(self) -> None:
        policy = PasswordPolicy()
        assert policy.min_length == 8
        assert policy.require_upper is True
        assert policy.max_age_days is None

    def test_custom_policy(self) -> None:
        policy = PasswordPolicy(min_length=12, max_age_days=90)
        assert policy.min_length == 12
        assert policy.max_age_days == 90

    def test_zero_min_length_raises(self) -> None:
        with pytest.raises(ValidationException):
            PasswordPolicy(min_length=0)

    def test_zero_max_age_raises(self) -> None:
        with pytest.raises(ValidationException):
            PasswordPolicy(max_age_days=0)

"""Unit-тесты для FailedLoginPolicy."""

import pytest

from app.shared.domain.exceptions import ValidationException
from app.context.identity.domain.value_objects.failed_login_policy import FailedLoginPolicy
from app.context.identity.domain.value_objects.lockout_threshold import LockoutThreshold


@pytest.mark.unit
class TestFailedLoginPolicy:
    def test_policy_with_thresholds(self) -> None:
        policy = FailedLoginPolicy(thresholds=[
            LockoutThreshold(failed_attempts=3, lock_duration_minutes=15),
            LockoutThreshold(failed_attempts=5, lock_duration_minutes=60),
        ])
        assert len(policy.thresholds) == 2

    def test_empty_thresholds_raises(self) -> None:
        with pytest.raises(ValidationException):
            FailedLoginPolicy(thresholds=[])

    def test_get_threshold_for_attempts(self) -> None:
        policy = FailedLoginPolicy(thresholds=[
            LockoutThreshold(failed_attempts=3, lock_duration_minutes=15),
            LockoutThreshold(failed_attempts=5, lock_duration_minutes=60),
        ])
        assert policy.get_threshold_for_attempts(2) is None
        assert policy.get_threshold_for_attempts(3).lock_duration_minutes == 15
        assert policy.get_threshold_for_attempts(5).lock_duration_minutes == 60
        assert policy.get_threshold_for_attempts(7).lock_duration_minutes == 60

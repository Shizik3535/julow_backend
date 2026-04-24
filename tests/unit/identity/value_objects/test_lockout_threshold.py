"""Unit-тесты для LockoutThreshold."""

import pytest

from app.shared.domain.exceptions import ValidationException
from app.context.identity.domain.value_objects.lockout_threshold import LockoutThreshold


@pytest.mark.unit
class TestLockoutThreshold:
    def test_valid_threshold(self) -> None:
        t = LockoutThreshold(failed_attempts=5, lock_duration_minutes=30)
        assert t.failed_attempts == 5
        assert t.lock_duration_minutes == 30

    def test_zero_attempts_raises(self) -> None:
        with pytest.raises(ValidationException):
            LockoutThreshold(failed_attempts=0, lock_duration_minutes=30)

    def test_zero_duration_raises(self) -> None:
        with pytest.raises(ValidationException):
            LockoutThreshold(failed_attempts=5, lock_duration_minutes=0)

    def test_equality(self) -> None:
        t1 = LockoutThreshold(failed_attempts=5, lock_duration_minutes=30)
        t2 = LockoutThreshold(failed_attempts=5, lock_duration_minutes=30)
        assert t1 == t2

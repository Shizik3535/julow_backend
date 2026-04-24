"""Unit-тесты для LoginAttempt."""

import pytest

from app.shared.domain.value_objects.ip_address_vo import IpAddress
from app.context.identity.domain.entities.login_attempt import LoginAttempt
from app.context.identity.domain.value_objects.login_status import LoginStatus


@pytest.mark.unit
class TestLoginAttempt:
    def test_create_failed_login_attempt(self) -> None:
        attempt = LoginAttempt(ip=IpAddress("192.168.1.1"), user_agent="Chrome", login_status=LoginStatus.FAILED)
        assert attempt.login_status == LoginStatus.FAILED
        assert not attempt.was_successful

    def test_create_successful_login_attempt(self) -> None:
        attempt = LoginAttempt(ip=IpAddress("192.168.1.1"), user_agent="Chrome", login_status=LoginStatus.SUCCESS)
        assert attempt.login_status == LoginStatus.SUCCESS
        assert attempt.was_successful

"""Unit-тесты для LoginStatus."""

import pytest

from app.context.identity.domain.value_objects.login_status import LoginStatus


@pytest.mark.unit
class TestLoginStatus:
    def test_all_statuses_exist(self) -> None:
        assert LoginStatus.SUCCESS.value == "success"
        assert LoginStatus.FAILED.value == "failed"
        assert LoginStatus.BLOCKED.value == "blocked"

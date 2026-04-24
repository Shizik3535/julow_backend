"""Unit-тесты для SessionStatus."""

import pytest

from app.context.identity.domain.value_objects.session_status import SessionStatus


@pytest.mark.unit
class TestSessionStatus:
    def test_all_statuses_exist(self) -> None:
        assert SessionStatus.ACTIVE.value == "active"
        assert SessionStatus.EXPIRED.value == "expired"
        assert SessionStatus.TERMINATED.value == "terminated"

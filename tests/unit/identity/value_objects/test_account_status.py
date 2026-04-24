"""Unit-тесты для AccountStatus."""

import pytest

from app.context.identity.domain.value_objects.account_status import AccountStatus


@pytest.mark.unit
class TestAccountStatus:
    def test_all_statuses_exist(self) -> None:
        assert AccountStatus.PENDING_VERIFICATION.value == "pending_verification"
        assert AccountStatus.ACTIVE.value == "active"
        assert AccountStatus.LOCKED.value == "locked"
        assert AccountStatus.DISABLED.value == "disabled"
        assert AccountStatus.PENDING_DELETION.value == "pending_deletion"

    def test_statuses_are_distinct(self) -> None:
        values = [s.value for s in AccountStatus]
        assert len(values) == len(set(values))

"""Unit-тесты для PinnedTargetType."""

import pytest

from app.context.profile.domain.value_objects.pinned_target_type import PinnedTargetType


@pytest.mark.unit
class TestPinnedTargetType:
    def test_all_types_exist(self) -> None:
        assert PinnedTargetType.WORKSPACE.value == "workspace"
        assert PinnedTargetType.PROJECT.value == "project"
        assert PinnedTargetType.TASK.value == "task"
        assert PinnedTargetType.DASHBOARD.value == "dashboard"
        assert PinnedTargetType.REPORT.value == "report"

    def test_types_are_distinct(self) -> None:
        values = [t.value for t in PinnedTargetType]
        assert len(values) == len(set(values))

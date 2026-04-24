"""Unit-тесты для ActualEffort (Task BC)."""

import pytest

from app.shared.domain.exceptions import ValidationException
from app.context.task.domain.value_objects.actual_effort import ActualEffort
from app.context.task.domain.value_objects.effort_unit import EffortUnit


@pytest.mark.unit
class TestActualEffort:
    def test_valid_value(self) -> None:
        vo = ActualEffort(value=5.0, unit=EffortUnit.HOURS)
        assert vo.value == 5.0
        assert vo.unit == EffortUnit.HOURS

    def test_zero_value(self) -> None:
        vo = ActualEffort(value=0.0)
        assert vo.value == 0.0

    def test_negative_raises(self) -> None:
        with pytest.raises(ValidationException) as exc_info:
            ActualEffort(value=-1.0)
        assert exc_info.value.field == "actual_effort"

    def test_frozen(self) -> None:
        vo = ActualEffort(value=5.0)
        with pytest.raises(AttributeError):
            vo.value = 0.0

    def test_equality_by_value(self) -> None:
        assert ActualEffort(value=5.0, unit=EffortUnit.HOURS) == ActualEffort(value=5.0, unit=EffortUnit.HOURS)

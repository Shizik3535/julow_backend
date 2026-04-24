"""Unit-тесты для EffortEstimate (Task BC)."""

import pytest

from app.shared.domain.exceptions import ValidationException
from app.context.task.domain.value_objects.effort_estimate import EffortEstimate
from app.context.task.domain.value_objects.effort_unit import EffortUnit


@pytest.mark.unit
class TestEffortEstimate:
    def test_valid_value(self) -> None:
        vo = EffortEstimate(value=8.0, unit=EffortUnit.HOURS)
        assert vo.value == 8.0
        assert vo.unit == EffortUnit.HOURS

    def test_zero_value(self) -> None:
        vo = EffortEstimate(value=0.0)
        assert vo.value == 0.0

    def test_negative_raises(self) -> None:
        with pytest.raises(ValidationException) as exc_info:
            EffortEstimate(value=-1.0)
        assert exc_info.value.field == "effort_estimate"

    def test_frozen(self) -> None:
        vo = EffortEstimate(value=8.0)
        with pytest.raises(AttributeError):
            vo.value = 0.0

    def test_equality_by_value(self) -> None:
        assert EffortEstimate(value=8.0, unit=EffortUnit.HOURS) == EffortEstimate(value=8.0, unit=EffortUnit.HOURS)

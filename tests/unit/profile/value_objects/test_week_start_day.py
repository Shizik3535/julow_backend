"""Unit-тесты для WeekStartDay."""

import pytest

from app.context.profile.domain.value_objects.week_start_day import WeekStartDay


@pytest.mark.unit
class TestWeekStartDay:
    def test_all_days_exist(self) -> None:
        assert WeekStartDay.MONDAY.value == "monday"
        assert WeekStartDay.SUNDAY.value == "sunday"
        assert WeekStartDay.SATURDAY.value == "saturday"

    def test_days_are_distinct(self) -> None:
        values = [d.value for d in WeekStartDay]
        assert len(values) == len(set(values))

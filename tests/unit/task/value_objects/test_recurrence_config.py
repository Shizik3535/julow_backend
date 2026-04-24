"""Unit-тесты для RecurrenceConfig (Task BC)."""

from datetime import date

import pytest

from app.shared.domain.exceptions import ValidationException
from app.context.task.domain.value_objects.recurrence_config import RecurrenceConfig
from app.context.task.domain.value_objects.recurrence_pattern import RecurrencePattern


@pytest.mark.unit
class TestRecurrenceConfig:
    def test_defaults(self) -> None:
        config = RecurrenceConfig()
        assert config.pattern == RecurrencePattern.WEEKLY
        assert config.interval == 1
        assert config.end_date is None
        assert config.max_occurrences is None

    def test_custom_values(self) -> None:
        end = date(2026, 12, 31)
        config = RecurrenceConfig(
            pattern=RecurrencePattern.DAILY,
            interval=2,
            end_date=end,
            max_occurrences=10,
        )
        assert config.pattern == RecurrencePattern.DAILY
        assert config.interval == 2
        assert config.end_date == end
        assert config.max_occurrences == 10

    def test_interval_less_than_1_raises(self) -> None:
        with pytest.raises(ValidationException) as exc_info:
            RecurrenceConfig(interval=0)
        assert exc_info.value.field == "recurrence_interval"

    def test_max_occurrences_less_than_1_raises(self) -> None:
        with pytest.raises(ValidationException) as exc_info:
            RecurrenceConfig(max_occurrences=0)
        assert exc_info.value.field == "recurrence_max_occurrences"

    def test_frozen(self) -> None:
        config = RecurrenceConfig()
        with pytest.raises(AttributeError):
            config.interval = 5

    def test_equality_by_value(self) -> None:
        assert RecurrenceConfig(pattern=RecurrencePattern.WEEKLY, interval=1) == RecurrenceConfig(pattern=RecurrencePattern.WEEKLY, interval=1)

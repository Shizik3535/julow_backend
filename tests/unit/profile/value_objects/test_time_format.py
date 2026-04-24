"""Unit-тесты для TimeFormat."""

import pytest

from app.context.profile.domain.value_objects.time_format import TimeFormat


@pytest.mark.unit
class TestTimeFormat:
    def test_all_formats_exist(self) -> None:
        assert TimeFormat.H24.value == "h24"
        assert TimeFormat.H12.value == "h12"

    def test_formats_are_distinct(self) -> None:
        values = [f.value for f in TimeFormat]
        assert len(values) == len(set(values))

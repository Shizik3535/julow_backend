"""Unit-тесты для DateFormat."""

import pytest

from app.shared.domain.exceptions import ValidationException
from app.context.profile.domain.value_objects.date_format import DateFormat, PRESET_DATE_FORMATS


@pytest.mark.unit
class TestDateFormat:
    def test_valid_iso_format(self) -> None:
        df = DateFormat("YYYY-MM-DD")
        assert df.value == "YYYY-MM-DD"

    def test_valid_eu_dots(self) -> None:
        df = DateFormat("DD.MM.YYYY")
        assert df.value == "DD.MM.YYYY"

    def test_valid_us_slashes(self) -> None:
        df = DateFormat("MM/DD/YYYY")
        assert df.value == "MM/DD/YYYY"

    def test_valid_asian_slashes(self) -> None:
        df = DateFormat("YYYY/MM/DD")
        assert df.value == "YYYY/MM/DD"

    def test_invalid_format_raises(self) -> None:
        with pytest.raises(ValidationException) as exc_info:
            DateFormat("invalid")
        assert exc_info.value.field == "date_format"

    def test_empty_raises(self) -> None:
        with pytest.raises(ValidationException):
            DateFormat("")

    def test_wrong_letter_count_raises(self) -> None:
        with pytest.raises(ValidationException):
            DateFormat("YY-MM-DD")

    def test_missing_day_raises(self) -> None:
        with pytest.raises(ValidationException):
            DateFormat("YYYY-MM-YY")

    def test_preset_formats_all_valid(self) -> None:
        for name, pattern in PRESET_DATE_FORMATS.items():
            df = DateFormat(pattern)
            assert df.value == pattern

    def test_frozen(self) -> None:
        df = DateFormat("YYYY-MM-DD")
        with pytest.raises(Exception):
            df.value = "DD.MM.YYYY"

    def test_equality_by_value(self) -> None:
        df1 = DateFormat("YYYY-MM-DD")
        df2 = DateFormat("YYYY-MM-DD")
        assert df1 == df2

    def test_str_returns_value(self) -> None:
        df = DateFormat("DD.MM.YYYY")
        assert str(df) == "DD.MM.YYYY"

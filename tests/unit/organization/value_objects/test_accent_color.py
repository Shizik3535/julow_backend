"""Unit-тесты для AccentColor (Organization BC)."""

import pytest

from app.shared.domain.exceptions import ValidationException
from app.context.organization.domain.value_objects.accent_color import AccentColor


@pytest.mark.unit
class TestAccentColor:
    def test_valid_hex(self) -> None:
        color = AccentColor("#FF5500")
        assert color.hex == "#FF5500"

    def test_normalizes_to_uppercase(self) -> None:
        color = AccentColor("#ff5500")
        assert color.hex == "#FF5500"

    def test_normalizes_whitespace(self) -> None:
        color = AccentColor("  #FF5500  ")
        assert color.hex == "#FF5500"

    def test_invalid_hex_raises(self) -> None:
        with pytest.raises(ValidationException) as exc_info:
            AccentColor("red")
        assert exc_info.value.field == "accent_color"

    def test_invalid_short_hex_raises(self) -> None:
        with pytest.raises(ValidationException) as exc_info:
            AccentColor("#FFF")
        assert exc_info.value.field == "accent_color"

    def test_frozen(self) -> None:
        color = AccentColor("#FF5500")
        with pytest.raises(AttributeError):
            color.hex = "#000000"  # type: ignore[misc]

    def test_equality_by_value(self) -> None:
        assert AccentColor("#FF5500") == AccentColor("#ff5500")

    def test_str_representation(self) -> None:
        assert str(AccentColor("#FF5500")) == "#FF5500"

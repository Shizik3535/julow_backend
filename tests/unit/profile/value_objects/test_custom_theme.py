"""Unit-тесты для CustomTheme."""

import pytest

from app.shared.domain.value_objects.color_vo import Color
from app.context.profile.domain.value_objects.custom_theme import CustomTheme


@pytest.mark.unit
class TestCustomTheme:
    def test_create_with_name(self) -> None:
        theme = CustomTheme(name="Ocean")
        assert theme.name == "Ocean"
        assert theme.colors == {}

    def test_create_with_colors(self) -> None:
        colors = {"background": Color("#1A1A2E"), "primary": Color("#6366F1")}
        theme = CustomTheme(name="Dark Ocean", colors=colors)
        assert theme.colors["background"] == Color("#1A1A2E")
        assert theme.colors["primary"] == Color("#6366F1")

    def test_frozen(self) -> None:
        theme = CustomTheme(name="Test")
        with pytest.raises(Exception):
            theme.name = "Changed"

    def test_equality_by_value(self) -> None:
        t1 = CustomTheme(name="A", colors={"bg": Color("#000000")})
        t2 = CustomTheme(name="A", colors={"bg": Color("#000000")})
        assert t1 == t2

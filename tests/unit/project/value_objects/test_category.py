"""Unit-тесты для Category (Project BC)."""

import pytest

from app.shared.domain.value_objects.color_vo import Color
from app.context.project.domain.value_objects.category import Category


@pytest.mark.unit
class TestCategory:
    def test_valid_value(self) -> None:
        vo = Category(name="Engineering")
        assert vo.name == "Engineering"

    def test_with_color(self) -> None:
        color = Color("#FF5500")
        vo = Category(name="Engineering", color=color)
        assert vo.color == color

    def test_default_color_is_none(self) -> None:
        vo = Category(name="Engineering")
        assert vo.color is None

    def test_frozen(self) -> None:
        vo = Category(name="Engineering")
        with pytest.raises(AttributeError):
            vo.name = "changed"  # type: ignore[misc]

    def test_equality_by_value(self) -> None:
        assert Category(name="A") == Category(name="A")

    def test_inequality_different_name(self) -> None:
        assert Category(name="A") != Category(name="B")

    def test_str_representation(self) -> None:
        assert str(Category(name="Engineering")) == "Engineering"

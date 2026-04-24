"""Unit-тесты для Label (Task BC)."""

import pytest

from app.context.task.domain.value_objects.label import Label
from app.shared.domain.value_objects.color_vo import Color


@pytest.mark.unit
class TestLabel:
    def test_create_with_name(self) -> None:
        label = Label(name="bug")
        assert label.name == "bug"
        assert label.color is None

    def test_create_with_color(self) -> None:
        color = Color("#FF0000")
        label = Label(name="bug", color=color)
        assert label.color == color

    def test_frozen(self) -> None:
        label = Label(name="bug")
        with pytest.raises(AttributeError):
            label.name = "feature"

    def test_equality_by_value(self) -> None:
        assert Label(name="bug") == Label(name="bug")

    def test_str_representation(self) -> None:
        assert str(Label(name="bug")) == "bug"

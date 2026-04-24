"""Unit-тесты для RetroSection (Project BC)."""

import pytest

from app.context.project.domain.value_objects.retro_section import RetroSection
from app.context.project.domain.value_objects.retro_item_type import RetroItemType


@pytest.mark.unit
class TestRetroSection:
    def test_create(self) -> None:
        vo = RetroSection(title="What went well")
        assert vo.title == "What went well"

    def test_defaults(self) -> None:
        vo = RetroSection(title="Test")
        assert vo.prompt is None
        assert vo.item_type == RetroItemType.NEUTRAL

    def test_custom_values(self) -> None:
        vo = RetroSection(
            title="Improvements",
            prompt="What can we do better?",
            item_type=RetroItemType.NEGATIVE,
        )
        assert vo.prompt == "What can we do better?"
        assert vo.item_type == RetroItemType.NEGATIVE

    def test_frozen(self) -> None:
        vo = RetroSection(title="Test")
        with pytest.raises(AttributeError):
            vo.title = "changed"  # type: ignore[misc]

    def test_equality_by_value(self) -> None:
        assert RetroSection(title="A") == RetroSection(title="A")

    def test_inequality_different_title(self) -> None:
        assert RetroSection(title="A") != RetroSection(title="B")

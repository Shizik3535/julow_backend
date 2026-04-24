"""Unit-тесты для CardAppearance (Project BC)."""

import pytest

from app.context.project.domain.value_objects.card_appearance import CardAppearance


@pytest.mark.unit
class TestCardAppearance:
    def test_defaults(self) -> None:
        vo = CardAppearance()
        assert vo.visible_fields == []
        assert not vo.compact_mode
        assert vo.show_cover_image

    def test_custom_values(self) -> None:
        vo = CardAppearance(
            visible_fields=["title", "assignee"],
            compact_mode=True,
            show_cover_image=False,
        )
        assert vo.visible_fields == ["title", "assignee"]
        assert vo.compact_mode
        assert not vo.show_cover_image

    def test_frozen(self) -> None:
        vo = CardAppearance()
        with pytest.raises(AttributeError):
            vo.compact_mode = True  # type: ignore[misc]

    def test_equality_by_value(self) -> None:
        assert CardAppearance() == CardAppearance()

    def test_inequality_different_fields(self) -> None:
        assert CardAppearance() != CardAppearance(compact_mode=True)

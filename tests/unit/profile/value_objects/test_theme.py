"""Unit-тесты для Theme."""

import pytest

from app.context.profile.domain.value_objects.theme import Theme


@pytest.mark.unit
class TestTheme:
    def test_all_themes_exist(self) -> None:
        assert Theme.LIGHT.value == "light"
        assert Theme.DARK.value == "dark"
        assert Theme.SYSTEM.value == "system"
        assert Theme.CUSTOM.value == "custom"

    def test_themes_are_distinct(self) -> None:
        values = [t.value for t in Theme]
        assert len(values) == len(set(values))

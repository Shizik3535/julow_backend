"""Unit-тесты для NavigationSettings."""

import pytest

from app.context.profile.domain.value_objects.navigation_settings import NavigationSettings
from app.context.profile.domain.value_objects.start_page import StartPage


@pytest.mark.unit
class TestNavigationSettings:
    def test_defaults(self) -> None:
        settings = NavigationSettings()
        assert settings.start_page == StartPage("dashboard")

    def test_custom_start_page(self) -> None:
        settings = NavigationSettings(start_page=StartPage("my_tasks"))
        assert settings.start_page == StartPage("my_tasks")

    def test_frozen(self) -> None:
        settings = NavigationSettings()
        with pytest.raises(Exception):
            settings.start_page = StartPage("inbox")

    def test_equality_by_value(self) -> None:
        s1 = NavigationSettings()
        s2 = NavigationSettings()
        assert s1 == s2

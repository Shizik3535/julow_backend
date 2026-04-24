"""Unit-тесты для AppearanceSettings."""

import pytest

from app.shared.domain.value_objects.color_vo import Color
from app.context.profile.domain.value_objects.appearance_settings import AppearanceSettings
from app.context.profile.domain.value_objects.theme import Theme
from app.context.profile.domain.value_objects.interface_density import InterfaceDensity
from app.context.profile.domain.value_objects.custom_theme import CustomTheme


@pytest.mark.unit
class TestAppearanceSettings:
    def test_defaults(self) -> None:
        settings = AppearanceSettings()
        assert settings.theme == Theme.SYSTEM
        assert settings.accent_color == Color("#6366F1")
        assert settings.custom_theme is None
        assert settings.interface_density == InterfaceDensity.COMFORTABLE

    def test_custom_theme_activated(self) -> None:
        custom = CustomTheme(name="Midnight", colors={"bg": Color("#000000")})
        settings = AppearanceSettings(theme=Theme.CUSTOM, custom_theme=custom)
        assert settings.theme == Theme.CUSTOM
        assert settings.custom_theme is not None
        assert settings.custom_theme.name == "Midnight"

    def test_frozen(self) -> None:
        settings = AppearanceSettings()
        with pytest.raises(Exception):
            settings.theme = Theme.DARK

    def test_equality_by_value(self) -> None:
        s1 = AppearanceSettings()
        s2 = AppearanceSettings()
        assert s1 == s2

    def test_clone_with_override(self) -> None:
        settings = AppearanceSettings()
        dark = settings.clone(theme=Theme.DARK)
        assert dark.theme == Theme.DARK
        assert settings.theme == Theme.SYSTEM

"""Unit-тесты для HotkeyConfig."""

import pytest

from app.context.profile.domain.value_objects.hotkey_config import HotkeyConfig
from app.context.profile.domain.value_objects.hotkey_action import HotkeyAction
from app.context.profile.domain.exceptions.profile_exceptions import InvalidHotkeyException


@pytest.mark.unit
class TestHotkeyConfig:
    def test_create_config(self) -> None:
        config = HotkeyConfig(action=HotkeyAction.SEARCH, key_combination="Ctrl+K", is_enabled=True)
        assert config.action == HotkeyAction.SEARCH
        assert config.key_combination == "Ctrl+K"
        assert config.is_enabled is True

    def test_disabled_config(self) -> None:
        config = HotkeyConfig(action=HotkeyAction.GO_HOME, key_combination="Alt+H", is_enabled=False)
        assert not config.is_enabled

    def test_frozen(self) -> None:
        config = HotkeyConfig(action=HotkeyAction.SEARCH, key_combination="Ctrl+K")
        with pytest.raises(Exception):
            config.key_combination = "Ctrl+Shift+K"

    def test_equality_by_value(self) -> None:
        c1 = HotkeyConfig(action=HotkeyAction.SEARCH, key_combination="Ctrl+K")
        c2 = HotkeyConfig(action=HotkeyAction.SEARCH, key_combination="Ctrl+K")
        assert c1 == c2

    def test_empty_key_combination_raises(self) -> None:
        with pytest.raises(InvalidHotkeyException):
            HotkeyConfig(action=HotkeyAction.SEARCH, key_combination="")

    def test_blank_key_combination_raises(self) -> None:
        with pytest.raises(InvalidHotkeyException):
            HotkeyConfig(action=HotkeyAction.SEARCH, key_combination="   ")

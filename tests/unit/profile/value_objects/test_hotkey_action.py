"""Unit-тесты для HotkeyAction."""

import pytest

from app.context.profile.domain.value_objects.hotkey_action import HotkeyAction


@pytest.mark.unit
class TestHotkeyAction:
    def test_all_actions_exist(self) -> None:
        assert HotkeyAction.CREATE_TASK.value == "create_task"
        assert HotkeyAction.NAVIGATE_INBOX.value == "navigate_inbox"
        assert HotkeyAction.SEARCH.value == "search"
        assert HotkeyAction.TOGGLE_SIDEBAR.value == "toggle_sidebar"
        assert HotkeyAction.GO_HOME.value == "go_home"
        assert HotkeyAction.QUICK_ACTION.value == "quick_action"

    def test_actions_are_distinct(self) -> None:
        values = [a.value for a in HotkeyAction]
        assert len(values) == len(set(values))

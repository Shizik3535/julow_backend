"""Unit-тесты для StartPage."""

import pytest

from app.shared.domain.exceptions import ValidationException
from app.context.profile.domain.value_objects.start_page import StartPage


@pytest.mark.unit
class TestStartPage:
    def test_valid_start_page(self) -> None:
        sp = StartPage("dashboard")
        assert sp.value == "dashboard"

    def test_various_valid_pages(self) -> None:
        for page in ["my_tasks", "inbox", "calendar", "reports", "team"]:
            sp = StartPage(page)
            assert sp.value == page

    def test_empty_raises(self) -> None:
        with pytest.raises(ValidationException) as exc_info:
            StartPage("")
        assert exc_info.value.field == "start_page"

    def test_whitespace_only_raises(self) -> None:
        with pytest.raises(ValidationException):
            StartPage("   ")

    def test_frozen(self) -> None:
        sp = StartPage("dashboard")
        with pytest.raises(Exception):
            sp.value = "inbox"

    def test_equality_by_value(self) -> None:
        sp1 = StartPage("dashboard")
        sp2 = StartPage("dashboard")
        assert sp1 == sp2

    def test_str_returns_value(self) -> None:
        sp = StartPage("dashboard")
        assert str(sp) == "dashboard"

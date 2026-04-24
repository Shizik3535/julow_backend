"""Unit-тесты для SortRule (Project BC)."""

import pytest

from app.context.project.domain.value_objects.sort_rule import SortRule
from app.context.project.domain.value_objects.sort_direction import SortDirection


@pytest.mark.unit
class TestSortRule:
    def test_create(self) -> None:
        vo = SortRule(field="priority")
        assert vo.field == "priority"

    def test_defaults(self) -> None:
        vo = SortRule(field="name")
        assert vo.direction == SortDirection.ASC

    def test_custom_direction(self) -> None:
        vo = SortRule(field="created_at", direction=SortDirection.DESC)
        assert vo.direction == SortDirection.DESC

    def test_frozen(self) -> None:
        vo = SortRule(field="name")
        with pytest.raises(AttributeError):
            vo.field = "changed"  # type: ignore[misc]

    def test_equality_by_value(self) -> None:
        assert SortRule(field="name") == SortRule(field="name")

    def test_inequality_different_field(self) -> None:
        assert SortRule(field="a") != SortRule(field="b")

"""Unit-тесты для ViewFilter (Project BC)."""

import pytest

from app.context.project.domain.value_objects.view_filter import ViewFilter
from app.context.project.domain.value_objects.filter_operator import FilterOperator


@pytest.mark.unit
class TestViewFilter:
    def test_create(self) -> None:
        vo = ViewFilter(field="status")
        assert vo.field == "status"

    def test_defaults(self) -> None:
        vo = ViewFilter(field="status")
        assert vo.operator == FilterOperator.EQ
        assert vo.value == ""

    def test_custom_values(self) -> None:
        vo = ViewFilter(field="assignee", operator=FilterOperator.IN, value="user-1")
        assert vo.operator == FilterOperator.IN
        assert vo.value == "user-1"

    def test_frozen(self) -> None:
        vo = ViewFilter(field="status")
        with pytest.raises(AttributeError):
            vo.field = "changed"  # type: ignore[misc]

    def test_equality_by_value(self) -> None:
        assert ViewFilter(field="a") == ViewFilter(field="a")

    def test_inequality_different_field(self) -> None:
        assert ViewFilter(field="a") != ViewFilter(field="b")

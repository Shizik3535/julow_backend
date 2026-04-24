"""Unit-тесты для CustomFieldDefinition (Project BC)."""

import pytest

from app.context.project.domain.value_objects.custom_field_definition import CustomFieldDefinition
from app.context.project.domain.value_objects.custom_field_type import CustomFieldType


@pytest.mark.unit
class TestCustomFieldDefinition:
    def test_defaults(self) -> None:
        vo = CustomFieldDefinition(name="priority")
        assert vo.name == "priority"
        assert vo.field_type == CustomFieldType.TEXT
        assert not vo.is_required
        assert vo.options is None
        assert vo.default_value is None
        assert vo.description is None

    def test_custom_values(self) -> None:
        vo = CustomFieldDefinition(
            name="status",
            field_type=CustomFieldType.SELECT,
            is_required=True,
            options=["open", "closed"],
            default_value="open",
            description="Task status",
        )
        assert vo.field_type == CustomFieldType.SELECT
        assert vo.is_required
        assert vo.options == ["open", "closed"]
        assert vo.default_value == "open"
        assert vo.description == "Task status"

    def test_frozen(self) -> None:
        vo = CustomFieldDefinition(name="priority")
        with pytest.raises(AttributeError):
            vo.name = "changed"  # type: ignore[misc]

    def test_equality_by_value(self) -> None:
        assert CustomFieldDefinition(name="x") == CustomFieldDefinition(name="x")

    def test_inequality_different_name(self) -> None:
        assert CustomFieldDefinition(name="a") != CustomFieldDefinition(name="b")

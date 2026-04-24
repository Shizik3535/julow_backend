"""Unit-тесты для TaskOrder (Task BC)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.domain.value_objects.task_order import TaskOrder


@pytest.mark.unit
class TestTaskOrder:
    def test_defaults(self) -> None:
        order = TaskOrder()
        assert order.position == 0.0
        assert order.column_id is not None

    def test_custom_values(self) -> None:
        column_id = Id.generate()
        order = TaskOrder(position=1.5, column_id=column_id)
        assert order.position == 1.5
        assert order.column_id == column_id

    def test_frozen(self) -> None:
        order = TaskOrder()
        with pytest.raises(AttributeError):
            order.position = 2.0

    def test_equality_by_value(self) -> None:
        column_id = Id.generate()
        assert TaskOrder(position=1.0, column_id=column_id) == TaskOrder(position=1.0, column_id=column_id)

"""Unit-тесты для TaskProgress (Task BC)."""

import pytest

from app.shared.domain.exceptions import ValidationException
from app.context.task.domain.value_objects.task_progress import TaskProgress


@pytest.mark.unit
class TestTaskProgress:
    def test_valid_value(self) -> None:
        vo = TaskProgress(value=50)
        assert vo.value == 50

    def test_zero_and_hundred(self) -> None:
        assert TaskProgress(value=0).value == 0
        assert TaskProgress(value=100).value == 100

    def test_negative_raises(self) -> None:
        with pytest.raises(ValidationException) as exc_info:
            TaskProgress(value=-1)
        assert exc_info.value.field == "task_progress"

    def test_over_100_raises(self) -> None:
        with pytest.raises(ValidationException) as exc_info:
            TaskProgress(value=101)
        assert exc_info.value.field == "task_progress"

    def test_frozen(self) -> None:
        vo = TaskProgress(value=50)
        with pytest.raises(AttributeError):
            vo.value = 0

    def test_equality_by_value(self) -> None:
        assert TaskProgress(value=50) == TaskProgress(value=50)

    def test_str_representation(self) -> None:
        assert str(TaskProgress(value=50)) == "50%"

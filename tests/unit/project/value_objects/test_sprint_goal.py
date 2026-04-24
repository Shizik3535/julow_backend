"""Unit-тесты для SprintGoal (Project BC)."""

import pytest

from app.context.project.domain.value_objects.sprint_goal import SprintGoal


@pytest.mark.unit
class TestSprintGoal:
    def test_valid_value(self) -> None:
        vo = SprintGoal(value="Deliver auth feature")
        assert vo.value == "Deliver auth feature"

    def test_frozen(self) -> None:
        vo = SprintGoal(value="Goal")
        with pytest.raises(AttributeError):
            vo.value = "changed"  # type: ignore[misc]

    def test_equality_by_value(self) -> None:
        assert SprintGoal(value="Goal") == SprintGoal(value="Goal")

    def test_inequality_different_value(self) -> None:
        assert SprintGoal(value="A") != SprintGoal(value="B")

    def test_str_representation(self) -> None:
        assert str(SprintGoal(value="My goal")) == "My goal"

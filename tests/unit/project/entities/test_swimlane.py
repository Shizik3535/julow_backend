"""Unit-тесты для Swimlane (Project BC)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.domain.entities.swimlane import Swimlane
from app.context.project.domain.value_objects.swimlane_group_by import SwimlaneGroupBy


@pytest.mark.unit
class TestSwimlane:
    def test_create(self) -> None:
        swimlane = Swimlane(name="By Assignee", order=0, group_by=SwimlaneGroupBy.ASSIGNEE)
        assert swimlane.name == "By Assignee"
        assert swimlane.order == 0
        assert swimlane.group_by == SwimlaneGroupBy.ASSIGNEE
        assert swimlane.id is not None
        assert swimlane.group_value is None

    def test_create_with_group_value(self) -> None:
        swimlane = Swimlane(name="Priority: High", order=1, group_by=SwimlaneGroupBy.PRIORITY, group_value="high")
        assert swimlane.group_value == "high"

    def test_equality_by_id(self) -> None:
        shared_id = Id.generate()
        s1 = Swimlane(id=shared_id, name="Row", order=0)
        s2 = Swimlane(id=shared_id, name="Row", order=0)
        assert s1 == s2

    def test_inequality_different_id(self) -> None:
        s1 = Swimlane(name="Row", order=0)
        s2 = Swimlane(name="Row", order=0)
        assert s1 != s2

"""Unit-тесты для Milestone (Project BC)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.domain.entities.milestone import Milestone
from app.context.project.domain.value_objects.milestone_status import MilestoneStatus


@pytest.mark.unit
class TestMilestone:
    def test_create(self) -> None:
        milestone = Milestone(name="v1.0")
        assert milestone.name == "v1.0"
        assert milestone.id is not None
        assert milestone.status == MilestoneStatus.NOT_STARTED
        assert milestone.description is None
        assert milestone.completed_at is None

    def test_equality_by_id(self) -> None:
        shared_id = Id.generate()
        m1 = Milestone(id=shared_id, name="v1.0")
        m2 = Milestone(id=shared_id, name="v1.0")
        assert m1 == m2

    def test_inequality_different_id(self) -> None:
        m1 = Milestone(name="v1.0")
        m2 = Milestone(name="v1.0")
        assert m1 != m2

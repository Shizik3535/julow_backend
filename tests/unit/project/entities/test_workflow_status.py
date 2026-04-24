"""Unit-тесты для WorkflowStatus (Project BC)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.domain.entities.workflow_status import WorkflowStatus
from app.context.project.domain.value_objects.workflow_status_category import WorkflowStatusCategory


@pytest.mark.unit
class TestWorkflowStatus:
    def test_create(self) -> None:
        status = WorkflowStatus(name="In Review", order=3, category=WorkflowStatusCategory.REVIEW)
        assert status.name == "In Review"
        assert status.order == 3
        assert status.category == WorkflowStatusCategory.REVIEW
        assert status.id is not None
        assert not status.is_default
        assert status.color is None
        assert status.icon is None

    def test_create_default_status(self) -> None:
        status = WorkflowStatus(name="To Do", order=0, is_default=True, category=WorkflowStatusCategory.TODO)
        assert status.is_default

    def test_equality_by_id(self) -> None:
        shared_id = Id.generate()
        s1 = WorkflowStatus(id=shared_id, name="To Do", order=0)
        s2 = WorkflowStatus(id=shared_id, name="To Do", order=0)
        assert s1 == s2

    def test_inequality_different_id(self) -> None:
        s1 = WorkflowStatus(name="To Do", order=0)
        s2 = WorkflowStatus(name="To Do", order=0)
        assert s1 != s2

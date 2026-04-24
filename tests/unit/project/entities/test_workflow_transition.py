"""Unit-тесты для WorkflowTransition (Project BC)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.domain.entities.workflow_transition import WorkflowTransition
from app.context.project.domain.value_objects.automation_trigger import AutomationTrigger


@pytest.mark.unit
class TestWorkflowTransition:
    def test_create(self) -> None:
        from_id = Id.generate()
        to_id = Id.generate()
        transition = WorkflowTransition(
            from_status_id=from_id,
            to_status_id=to_id,
            name="Start Work",
        )
        assert transition.from_status_id == from_id
        assert transition.to_status_id == to_id
        assert transition.name == "Start Work"
        assert transition.id is not None
        assert transition.trigger is None
        assert transition.required_permission is None

    def test_create_with_trigger_and_permission(self) -> None:
        transition = WorkflowTransition(
            from_status_id=Id.generate(),
            to_status_id=Id.generate(),
            name="Approve",
            trigger=AutomationTrigger.STATUS_CHANGED,
            required_permission="task:approve",
        )
        assert transition.trigger == AutomationTrigger.STATUS_CHANGED
        assert transition.required_permission == "task:approve"

    def test_equality_by_id(self) -> None:
        shared_id = Id.generate()
        from_id = Id.generate()
        to_id = Id.generate()
        t1 = WorkflowTransition(id=shared_id, from_status_id=from_id, to_status_id=to_id, name="Move")
        t2 = WorkflowTransition(id=shared_id, from_status_id=from_id, to_status_id=to_id, name="Move")
        assert t1 == t2

    def test_inequality_different_id(self) -> None:
        t1 = WorkflowTransition(name="Move")
        t2 = WorkflowTransition(name="Move")
        assert t1 != t2

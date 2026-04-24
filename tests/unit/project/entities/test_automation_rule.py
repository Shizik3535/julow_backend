"""Unit-тесты для AutomationRule (Project BC)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.domain.entities.automation_rule import AutomationRule
from app.context.project.domain.value_objects.automation_trigger import AutomationTrigger
from app.context.project.domain.value_objects.automation_action import AutomationAction


@pytest.mark.unit
class TestAutomationRule:
    def test_create(self) -> None:
        rule = AutomationRule(
            name="Auto-assign",
            trigger=AutomationTrigger.STATUS_CHANGED,
            action=AutomationAction.ASSIGN_USER,
        )
        assert rule.name == "Auto-assign"
        assert rule.trigger == AutomationTrigger.STATUS_CHANGED
        assert rule.action == AutomationAction.ASSIGN_USER
        assert rule.id is not None
        assert rule.is_enabled
        assert rule.action_params == {}

    def test_create_with_params(self) -> None:
        rule = AutomationRule(
            name="Auto-move",
            trigger=AutomationTrigger.PRIORITY_CHANGED,
            action=AutomationAction.MOVE_TO_SPRINT,
            action_params={"sprint_id": "abc-123"},
        )
        assert rule.action_params == {"sprint_id": "abc-123"}

    def test_equality_by_id(self) -> None:
        shared_id = Id.generate()
        r1 = AutomationRule(id=shared_id, name="Rule")
        r2 = AutomationRule(id=shared_id, name="Rule")
        assert r1 == r2

    def test_inequality_different_id(self) -> None:
        r1 = AutomationRule(name="Rule")
        r2 = AutomationRule(name="Rule")
        assert r1 != r2

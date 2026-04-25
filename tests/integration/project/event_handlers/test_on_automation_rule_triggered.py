"""Интеграционные тесты OnAutomationRuleTriggered (реальные repos)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.base_domain_event import BaseDomainEvent
from app.context.project.application.event_handlers.on_automation_rule_triggered import (
    OnAutomationRuleTriggered,
)
from tests.integration.project.conftest import _NoopEventBus


class _FakeEventWithProjectId(BaseDomainEvent):
    project_id: str = ""

    def __init__(self, project_id: str) -> None:
        super().__init__()
        self.project_id = project_id


class _FakeEventWithoutProjectId(BaseDomainEvent):
    pass


@pytest.mark.integration
class TestOnAutomationRuleTriggered:
    """Тесты OnAutomationRuleTriggered — intra-BC event handler."""

    @pytest.fixture
    def handler(self, board_repo) -> OnAutomationRuleTriggered:
        return OnAutomationRuleTriggered(board_repo=board_repo)

    async def test_triggers_matching_rule(self, handler, board_repo, make_project_with_membership) -> None:
        data = await make_project_with_membership()
        project = data["project"]
        board = data["board"]

        from app.context.project.domain.value_objects.automation_trigger import AutomationTrigger
        from app.context.project.domain.value_objects.automation_action import AutomationAction
        board.add_automation_rule(
            name="Auto Rule",
            trigger=AutomationTrigger.STATUS_CHANGED,
            action=AutomationAction.ASSIGN_USER,
            action_params={},
        )
        board.clear_domain_events()
        await board_repo.update(board)

        event = _FakeEventWithProjectId(project_id=str(project.id))
        # Should not raise
        await handler.handle(event)

    async def test_no_board_noop(self, handler) -> None:
        event = _FakeEventWithProjectId(project_id=str(Id.generate()))
        # Should not raise
        await handler.handle(event)

    async def test_no_project_id_noop(self, handler) -> None:
        event = _FakeEventWithoutProjectId()
        # Should not raise
        await handler.handle(event)

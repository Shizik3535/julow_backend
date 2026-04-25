"""Интеграционные тесты RemoveAutomationRuleHandler (реальные repos + реальные порты)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.commands.remove_automation_rule import (
    RemoveAutomationRuleCommand,
    RemoveAutomationRuleHandler,
)
from app.context.project.application.exceptions.board_app_exceptions import BoardNotFoundException
from tests.integration.project.conftest import (
    _AlwaysAllowProjectPermissionChecker,
    _NoopEventBus,
)


@pytest.mark.integration
class TestRemoveAutomationRuleHandler:
    """Тесты RemoveAutomationRuleHandler."""

    @pytest.fixture
    def handler(self, board_repo, permission_checker_stub, event_bus_stub) -> RemoveAutomationRuleHandler:
        return RemoveAutomationRuleHandler(
            board_repo=board_repo,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_remove_automation_rule_success(self, handler, board_repo, make_project_with_membership) -> None:
        data = await make_project_with_membership()
        project = data["project"]
        board = data["board"]

        from app.context.project.domain.value_objects.automation_trigger import AutomationTrigger
        from app.context.project.domain.value_objects.automation_action import AutomationAction
        board.add_automation_rule(
            name="ToDelete",
            trigger=AutomationTrigger.STATUS_CHANGED,
            action=AutomationAction.ASSIGN_USER,
            action_params={},
        )
        board.clear_domain_events()
        await board_repo.update(board)

        rule_id = board.automation_rules[-1].id
        cmd = RemoveAutomationRuleCommand(
            caller_id=str(data["owner_id"]),
            project_id=str(project.id),
            rule_id=str(rule_id),
        )
        await handler.handle(cmd)

        found = await board_repo.get_by_id(board.id)
        assert found is not None

    async def test_remove_automation_rule_board_not_found(self, handler) -> None:
        cmd = RemoveAutomationRuleCommand(
            caller_id=str(Id.generate()),
            project_id=str(Id.generate()),
            rule_id=str(Id.generate()),
        )
        with pytest.raises(BoardNotFoundException):
            await handler.handle(cmd)

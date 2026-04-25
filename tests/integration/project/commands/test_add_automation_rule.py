"""Интеграционные тесты AddAutomationRuleHandler (реальные repos + реальные порты)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.commands.add_automation_rule import (
    AddAutomationRuleCommand,
    AddAutomationRuleHandler,
)
from app.context.project.application.exceptions.board_app_exceptions import BoardNotFoundException
from tests.integration.project.conftest import (
    _AlwaysAllowProjectPermissionChecker,
    _NoopEventBus,
)


@pytest.mark.integration
class TestAddAutomationRuleHandler:
    """Тесты AddAutomationRuleHandler."""

    @pytest.fixture
    def handler(self, board_repo, permission_checker_stub, event_bus_stub) -> AddAutomationRuleHandler:
        return AddAutomationRuleHandler(
            board_repo=board_repo,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_add_automation_rule_success(self, handler, board_repo, make_project_with_membership) -> None:
        data = await make_project_with_membership()
        project = data["project"]

        cmd = AddAutomationRuleCommand(
            caller_id=str(data["owner_id"]),
            project_id=str(project.id),
            name="Auto-assign",
            trigger="status_changed",
            action="assign_user",
            action_params={"assignee": "creator"},
        )
        await handler.handle(cmd)

        board = await board_repo.get_by_project_id(project.id)
        assert board is not None
        assert any(r.name == "Auto-assign" for r in board.automation_rules)

    async def test_add_automation_rule_board_not_found(self, handler) -> None:
        cmd = AddAutomationRuleCommand(
            caller_id=str(Id.generate()),
            project_id=str(Id.generate()),
            name="X",
            trigger="status_changed",
            action="assign_user",
        )
        with pytest.raises(BoardNotFoundException):
            await handler.handle(cmd)

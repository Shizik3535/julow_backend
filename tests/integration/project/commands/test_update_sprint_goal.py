"""Интеграционные тесты UpdateSprintGoalHandler (реальные repos + реальные порты)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.commands.update_sprint_goal import (
    UpdateSprintGoalCommand,
    UpdateSprintGoalHandler,
)
from tests.integration.project.conftest import (
    _AlwaysAllowProjectPermissionChecker,
    _NoopEventBus,
)


@pytest.mark.integration
class TestUpdateSprintGoalHandler:
    """Тесты UpdateSprintGoalHandler."""

    @pytest.fixture
    def handler(self, sprint_repo, permission_checker_stub, event_bus_stub) -> UpdateSprintGoalHandler:
        return UpdateSprintGoalHandler(
            sprint_repo=sprint_repo,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_update_sprint_goal_success(self, handler, sprint_repo, make_sprint) -> None:
        sprint = await make_sprint()
        cmd = UpdateSprintGoalCommand(
            caller_id=str(Id.generate()),
            sprint_id=str(sprint.id),
            goal="New goal",
        )
        await handler.handle(cmd)

        found = await sprint_repo.get_by_id(sprint.id)
        assert found is not None
        assert found.goal is not None
        assert found.goal.value == "New goal"

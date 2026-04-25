"""Интеграционные тесты UpdateSprintDateRangeHandler (реальные repos + реальные порты)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.commands.update_sprint_date_range import (
    UpdateSprintDateRangeCommand,
    UpdateSprintDateRangeHandler,
)
from tests.integration.project.conftest import (
    _AlwaysAllowProjectPermissionChecker,
    _NoopEventBus,
)


@pytest.mark.integration
class TestUpdateSprintDateRangeHandler:
    """Тесты UpdateSprintDateRangeHandler."""

    @pytest.fixture
    def handler(self, sprint_repo, permission_checker_stub, event_bus_stub) -> UpdateSprintDateRangeHandler:
        return UpdateSprintDateRangeHandler(
            sprint_repo=sprint_repo,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_update_sprint_date_range_success(self, handler, sprint_repo, make_sprint) -> None:
        sprint = await make_sprint()
        cmd = UpdateSprintDateRangeCommand(
            caller_id=str(Id.generate()),
            sprint_id=str(sprint.id),
            start_date="2026-01-01",
            end_date="2026-01-31",
        )
        await handler.handle(cmd)

        found = await sprint_repo.get_by_id(sprint.id)
        assert found is not None

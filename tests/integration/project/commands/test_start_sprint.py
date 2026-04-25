"""Интеграционные тесты StartSprintHandler (реальные repos + реальные порты)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.commands.start_sprint import (
    StartSprintCommand,
    StartSprintHandler,
)
from app.context.project.domain.exceptions.sprint_exceptions import SprintNotFoundException
from app.context.project.domain.value_objects.sprint_status import SprintStatus
from tests.integration.project.conftest import (
    _AlwaysAllowProjectPermissionChecker,
    _NoopEventBus,
)


@pytest.mark.integration
class TestStartSprintHandler:
    """Тесты StartSprintHandler."""

    @pytest.fixture
    def handler(self, sprint_repo, permission_checker_stub, event_bus_stub) -> StartSprintHandler:
        return StartSprintHandler(
            sprint_repo=sprint_repo,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_start_sprint_success(self, handler, sprint_repo, make_sprint) -> None:
        sprint = await make_sprint()
        cmd = StartSprintCommand(
            caller_id=str(Id.generate()),
            sprint_id=str(sprint.id),
        )
        await handler.handle(cmd)

        found = await sprint_repo.get_by_id(sprint.id)
        assert found is not None
        assert found.status == SprintStatus.ACTIVE

    async def test_start_sprint_not_found(self, handler) -> None:
        cmd = StartSprintCommand(
            caller_id=str(Id.generate()),
            sprint_id=str(Id.generate()),
        )
        with pytest.raises(SprintNotFoundException):
            await handler.handle(cmd)

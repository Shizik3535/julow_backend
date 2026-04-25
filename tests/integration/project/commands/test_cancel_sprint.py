"""Интеграционные тесты CancelSprintHandler (реальные repos + реальные порты)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.commands.cancel_sprint import (
    CancelSprintCommand,
    CancelSprintHandler,
)
from app.context.project.domain.value_objects.sprint_status import SprintStatus
from tests.integration.project.conftest import (
    _AlwaysAllowProjectPermissionChecker,
    _NoopEventBus,
)


@pytest.mark.integration
class TestCancelSprintHandler:
    """Тесты CancelSprintHandler."""

    @pytest.fixture
    def handler(self, sprint_repo, permission_checker_stub, event_bus_stub) -> CancelSprintHandler:
        return CancelSprintHandler(
            sprint_repo=sprint_repo,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_cancel_sprint_success(self, handler, sprint_repo, make_sprint) -> None:
        sprint = await make_sprint()
        sprint.start()
        sprint.clear_domain_events()
        await sprint_repo.update(sprint)

        cmd = CancelSprintCommand(
            caller_id=str(Id.generate()),
            sprint_id=str(sprint.id),
        )
        await handler.handle(cmd)

        found = await sprint_repo.get_by_id(sprint.id)
        assert found is not None
        assert found.status == SprintStatus.CANCELLED

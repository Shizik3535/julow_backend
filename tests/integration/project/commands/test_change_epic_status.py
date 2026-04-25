"""Интеграционные тесты ChangeEpicStatusHandler (реальные repos + реальные порты)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.commands.change_epic_status import (
    ChangeEpicStatusCommand,
    ChangeEpicStatusHandler,
)
from app.context.project.domain.exceptions.epic_exceptions import EpicNotFoundException
from app.context.project.domain.value_objects.epic_status import EpicStatus
from tests.integration.project.conftest import (
    _AlwaysAllowProjectPermissionChecker,
    _NoopEventBus,
)


@pytest.mark.integration
class TestChangeEpicStatusHandler:
    """Тесты ChangeEpicStatusHandler."""

    @pytest.fixture
    def handler(self, epic_repo, permission_checker_stub, event_bus_stub) -> ChangeEpicStatusHandler:
        return ChangeEpicStatusHandler(
            epic_repo=epic_repo,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_change_epic_status_success(self, handler, epic_repo, make_epic) -> None:
        epic = await make_epic()
        cmd = ChangeEpicStatusCommand(
            caller_id=str(Id.generate()),
            epic_id=str(epic.id),
            new_status="in_progress",
        )
        await handler.handle(cmd)

        found = await epic_repo.get_by_id(epic.id)
        assert found is not None
        assert found.status == EpicStatus.IN_PROGRESS

    async def test_change_epic_status_not_found(self, handler) -> None:
        cmd = ChangeEpicStatusCommand(
            caller_id=str(Id.generate()),
            epic_id=str(Id.generate()),
            new_status="in_progress",
        )
        with pytest.raises(EpicNotFoundException):
            await handler.handle(cmd)

"""Интеграционные тесты UpdateEpicHandler (реальные repos + реальные порты)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.commands.update_epic import (
    UpdateEpicCommand,
    UpdateEpicHandler,
)
from app.context.project.domain.exceptions.epic_exceptions import EpicNotFoundException
from tests.integration.project.conftest import (
    _AlwaysAllowProjectPermissionChecker,
    _NoopEventBus,
)


@pytest.mark.integration
class TestUpdateEpicHandler:
    """Тесты UpdateEpicHandler."""

    @pytest.fixture
    def handler(self, epic_repo, permission_checker_stub, event_bus_stub) -> UpdateEpicHandler:
        return UpdateEpicHandler(
            epic_repo=epic_repo,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_update_epic_name(self, handler, epic_repo, make_epic) -> None:
        epic = await make_epic(name="Old Epic")
        cmd = UpdateEpicCommand(
            epic_id=str(epic.id),
            caller_id=str(Id.generate()),
            name="New Epic",
        )
        await handler.handle(cmd)

        found = await epic_repo.get_by_id(epic.id)
        assert found is not None
        assert found.name == "New Epic"

    async def test_update_epic_not_found(self, handler) -> None:
        cmd = UpdateEpicCommand(
            epic_id=str(Id.generate()),
            caller_id=str(Id.generate()),
            name="X",
        )
        with pytest.raises(EpicNotFoundException):
            await handler.handle(cmd)

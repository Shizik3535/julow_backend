"""Интеграционные тесты CreateEpicHandler (реальные repos + реальные порты)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.commands.create_epic import (
    CreateEpicCommand,
    CreateEpicHandler,
)
from app.context.project.domain.value_objects.epic_status import EpicStatus
from tests.integration.project.conftest import (
    _AlwaysAllowProjectPermissionChecker,
    _NoopEventBus,
)


@pytest.mark.integration
class TestCreateEpicHandler:
    """Тесты CreateEpicHandler."""

    @pytest.fixture
    def handler(self, project_repo, epic_repo, permission_checker_stub, event_bus_stub) -> CreateEpicHandler:
        return CreateEpicHandler(
            project_repo=project_repo,
            epic_repo=epic_repo,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_create_epic_success(self, handler, epic_repo, make_project) -> None:
        project = await make_project()
        cmd = CreateEpicCommand(
            caller_id=str(Id.generate()),
            project_id=str(project.id),
            name="Feature Epic",
        )
        result = await handler.handle(cmd)

        assert result.name == "Feature Epic"
        assert result.status == EpicStatus.OPEN.value

        epic = await epic_repo.get_by_id(Id.from_string(result.id))
        assert epic is not None

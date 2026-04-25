"""Интеграционные тесты CreateSprintHandler (реальные repos + реальные порты)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.commands.create_sprint import (
    CreateSprintCommand,
    CreateSprintHandler,
)
from app.context.project.domain.value_objects.methodology import Methodology
from app.context.project.domain.value_objects.sprint_status import SprintStatus
from tests.integration.project.conftest import (
    _AlwaysAllowProjectPermissionChecker,
    _NoopEventBus,
)


@pytest.mark.integration
class TestCreateSprintHandler:
    """Тесты CreateSprintHandler."""

    @pytest.fixture
    def handler(self, project_repo, sprint_repo, permission_checker_stub, event_bus_stub) -> CreateSprintHandler:
        return CreateSprintHandler(
            project_repo=project_repo,
            sprint_repo=sprint_repo,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_create_sprint_success(self, handler, sprint_repo, make_project) -> None:
        project = await make_project(methodology=Methodology.SCRUM)
        cmd = CreateSprintCommand(
            caller_id=str(Id.generate()),
            project_id=str(project.id),
            name="Sprint 1",
            goal="Ship feature X",
        )
        result = await handler.handle(cmd)

        assert result.name == "Sprint 1"
        assert result.status == SprintStatus.PLANNING.value

        sprint = await sprint_repo.get_by_id(Id.from_string(result.id))
        assert sprint is not None

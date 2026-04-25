"""Интеграционные тесты AddProjectMilestoneHandler (реальные repos + реальные порты)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.commands.add_project_milestone import (
    AddProjectMilestoneCommand,
    AddProjectMilestoneHandler,
)
from app.context.project.domain.exceptions.project_exceptions import ProjectNotFoundException
from tests.integration.project.conftest import (
    _AlwaysAllowProjectPermissionChecker,
    _NoopEventBus,
)


@pytest.mark.integration
class TestAddProjectMilestoneHandler:
    """Тесты AddProjectMilestoneHandler."""

    @pytest.fixture
    def handler(self, project_repo, permission_checker_stub, event_bus_stub) -> AddProjectMilestoneHandler:
        return AddProjectMilestoneHandler(
            project_repo=project_repo,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_add_milestone_success(self, handler, project_repo, make_project) -> None:
        from app.context.project.domain.value_objects.methodology import Methodology
        project = await make_project(methodology=Methodology.WATERFALL)
        cmd = AddProjectMilestoneCommand(
            caller_id=str(Id.generate()),
            project_id=str(project.id),
            name="v1.0 Release",
            due_date="2026-12-31",
        )
        result = await handler.handle(cmd)
        assert result.name == "v1.0 Release"

    async def test_add_milestone_not_found(self, handler) -> None:
        cmd = AddProjectMilestoneCommand(
            caller_id=str(Id.generate()),
            project_id=str(Id.generate()),
            name="X",
            due_date="2026-12-31",
        )
        with pytest.raises(ProjectNotFoundException):
            await handler.handle(cmd)

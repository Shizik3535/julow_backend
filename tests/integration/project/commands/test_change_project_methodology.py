"""Интеграционные тесты ChangeProjectMethodologyHandler (реальные repos + реальные порты)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.commands.change_project_methodology import (
    ChangeProjectMethodologyCommand,
    ChangeProjectMethodologyHandler,
)
from app.context.project.domain.exceptions.project_exceptions import ProjectNotFoundException
from app.context.project.domain.value_objects.methodology import Methodology
from tests.integration.project.conftest import (
    _AlwaysAllowProjectPermissionChecker,
    _NoopEventBus,
)


@pytest.mark.integration
class TestChangeProjectMethodologyHandler:
    """Тесты ChangeProjectMethodologyHandler."""

    @pytest.fixture
    def handler(self, project_repo, sprint_repo, permission_checker_stub, event_bus_stub) -> ChangeProjectMethodologyHandler:
        return ChangeProjectMethodologyHandler(
            project_repo=project_repo,
            sprint_repo=sprint_repo,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_change_methodology_success(self, handler, project_repo, make_project) -> None:
        project = await make_project(methodology=Methodology.KANBAN)
        cmd = ChangeProjectMethodologyCommand(
            caller_id=str(Id.generate()),
            project_id=str(project.id),
            new_methodology="scrum",
        )
        await handler.handle(cmd)

        found = await project_repo.get_by_id(project.id)
        assert found is not None
        assert found.methodology == Methodology.SCRUM

    async def test_change_methodology_not_found(self, handler) -> None:
        cmd = ChangeProjectMethodologyCommand(
            caller_id=str(Id.generate()),
            project_id=str(Id.generate()),
            new_methodology="scrum",
        )
        with pytest.raises(ProjectNotFoundException):
            await handler.handle(cmd)

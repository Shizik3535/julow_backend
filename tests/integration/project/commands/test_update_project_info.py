"""Интеграционные тесты UpdateProjectInfoHandler (реальные repos + реальные порты)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.commands.update_project_info import (
    UpdateProjectInfoCommand,
    UpdateProjectInfoHandler,
)
from app.context.project.domain.exceptions.project_exceptions import ProjectNotFoundException
from tests.integration.project.conftest import (
    _AlwaysAllowProjectPermissionChecker,
    _NoopEventBus,
)


@pytest.mark.integration
class TestUpdateProjectInfoHandler:
    """Тесты UpdateProjectInfoHandler."""

    @pytest.fixture
    def handler(self, project_repo, permission_checker_stub, event_bus_stub) -> UpdateProjectInfoHandler:
        return UpdateProjectInfoHandler(
            project_repo=project_repo,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_update_project_name(self, handler, project_repo, make_project) -> None:
        project = await make_project(name="Old Name")
        cmd = UpdateProjectInfoCommand(
            caller_id=str(Id.generate()),
            project_id=str(project.id),
            name="New Name",
        )
        await handler.handle(cmd)

        found = await project_repo.get_by_id(project.id)
        assert found is not None
        assert found.name == "New Name"

    async def test_update_project_not_found(self, handler) -> None:
        cmd = UpdateProjectInfoCommand(
            caller_id=str(Id.generate()),
            project_id=str(Id.generate()),
            name="X",
        )
        with pytest.raises(ProjectNotFoundException):
            await handler.handle(cmd)

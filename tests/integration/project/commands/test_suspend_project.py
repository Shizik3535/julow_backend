"""Интеграционные тесты SuspendProjectHandler (реальные repos + реальные порты)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.commands.suspend_project import (
    SuspendProjectCommand,
    SuspendProjectHandler,
)
from app.context.project.domain.exceptions.project_exceptions import ProjectNotFoundException
from app.context.project.domain.value_objects.project_status import ProjectStatus
from tests.integration.project.conftest import (
    _AlwaysAllowProjectPermissionChecker,
    _NoopEventBus,
)


@pytest.mark.integration
class TestSuspendProjectHandler:
    """Тесты SuspendProjectHandler."""

    @pytest.fixture
    def handler(self, project_repo, permission_checker_stub, event_bus_stub) -> SuspendProjectHandler:
        return SuspendProjectHandler(
            project_repo=project_repo,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_suspend_project_success(self, handler, project_repo, make_project) -> None:
        project = await make_project()
        cmd = SuspendProjectCommand(
            caller_id=str(Id.generate()),
            project_id=str(project.id),
            reason="Maintenance",
        )
        await handler.handle(cmd)

        found = await project_repo.get_by_id(project.id)
        assert found is not None
        assert found.status == ProjectStatus.SUSPENDED

    async def test_suspend_project_not_found(self, handler) -> None:
        cmd = SuspendProjectCommand(
            caller_id=str(Id.generate()),
            project_id=str(Id.generate()),
            reason="X",
        )
        with pytest.raises(ProjectNotFoundException):
            await handler.handle(cmd)

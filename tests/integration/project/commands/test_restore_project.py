"""Интеграционные тесты RestoreProjectHandler (реальные repos + реальные порты)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.commands.restore_project import (
    RestoreProjectCommand,
    RestoreProjectHandler,
)
from app.context.project.domain.exceptions.project_exceptions import ProjectNotFoundException
from app.context.project.domain.value_objects.project_status import ProjectStatus
from tests.integration.project.conftest import (
    _AlwaysAllowProjectPermissionChecker,
    _NoopEventBus,
)


@pytest.mark.integration
class TestRestoreProjectHandler:
    """Тесты RestoreProjectHandler."""

    @pytest.fixture
    def handler(self, project_repo, permission_checker_stub, event_bus_stub) -> RestoreProjectHandler:
        return RestoreProjectHandler(
            project_repo=project_repo,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_restore_project_success(self, handler, project_repo, make_project) -> None:
        project = await make_project()
        project.archive()
        project.clear_domain_events()
        await project_repo.update(project)

        cmd = RestoreProjectCommand(
            caller_id=str(Id.generate()),
            project_id=str(project.id),
        )
        await handler.handle(cmd)

        found = await project_repo.get_by_id(project.id)
        assert found is not None
        assert found.status == ProjectStatus.ACTIVE

    async def test_restore_project_not_found(self, handler) -> None:
        cmd = RestoreProjectCommand(
            caller_id=str(Id.generate()),
            project_id=str(Id.generate()),
        )
        with pytest.raises(ProjectNotFoundException):
            await handler.handle(cmd)

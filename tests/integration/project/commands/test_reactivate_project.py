"""Интеграционные тесты ReactivateProjectHandler (реальные repos + реальные порты)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.commands.reactivate_project import (
    ReactivateProjectCommand,
    ReactivateProjectHandler,
)
from app.context.project.domain.exceptions.project_exceptions import ProjectNotFoundException
from app.context.project.domain.value_objects.project_status import ProjectStatus
from tests.integration.project.conftest import (
    _AlwaysAllowProjectPermissionChecker,
    _NoopEventBus,
)


@pytest.mark.integration
class TestReactivateProjectHandler:
    """Тесты ReactivateProjectHandler."""

    @pytest.fixture
    def handler(self, project_repo, permission_checker_stub, event_bus_stub) -> ReactivateProjectHandler:
        return ReactivateProjectHandler(
            project_repo=project_repo,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_reactivate_project_success(self, handler, project_repo, make_project) -> None:
        project = await make_project()
        project.suspend(reason="Test")
        project.clear_domain_events()
        await project_repo.update(project)

        cmd = ReactivateProjectCommand(
            caller_id=str(Id.generate()),
            project_id=str(project.id),
        )
        await handler.handle(cmd)

        found = await project_repo.get_by_id(project.id)
        assert found is not None
        assert found.status == ProjectStatus.ACTIVE

    async def test_reactivate_project_not_found(self, handler) -> None:
        cmd = ReactivateProjectCommand(
            caller_id=str(Id.generate()),
            project_id=str(Id.generate()),
        )
        with pytest.raises(ProjectNotFoundException):
            await handler.handle(cmd)

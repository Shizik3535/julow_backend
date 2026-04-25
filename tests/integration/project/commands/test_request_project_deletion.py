"""Интеграционные тесты RequestProjectDeletionHandler (реальные repos + реальные порты)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.commands.request_project_deletion import (
    RequestProjectDeletionCommand,
    RequestProjectDeletionHandler,
)
from app.context.project.domain.exceptions.project_exceptions import ProjectNotFoundException
from tests.integration.project.conftest import (
    _AlwaysAllowProjectPermissionChecker,
    _NoopEventBus,
)


@pytest.mark.integration
class TestRequestProjectDeletionHandler:
    """Тесты RequestProjectDeletionHandler."""

    @pytest.fixture
    def handler(self, project_repo, permission_checker_stub, event_bus_stub) -> RequestProjectDeletionHandler:
        return RequestProjectDeletionHandler(
            project_repo=project_repo,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_request_project_deletion_success(self, handler, project_repo, make_project) -> None:
        project = await make_project()
        cmd = RequestProjectDeletionCommand(
            caller_id=str(Id.generate()),
            project_id=str(project.id),
        )
        await handler.handle(cmd)

        found = await project_repo.get_by_id(project.id)
        assert found is not None

    async def test_request_project_deletion_not_found(self, handler) -> None:
        cmd = RequestProjectDeletionCommand(
            caller_id=str(Id.generate()),
            project_id=str(Id.generate()),
        )
        with pytest.raises(ProjectNotFoundException):
            await handler.handle(cmd)

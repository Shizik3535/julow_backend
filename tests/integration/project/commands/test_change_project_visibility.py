"""Интеграционные тесты ChangeProjectVisibilityHandler (реальные repos + реальные порты)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.commands.change_project_visibility import (
    ChangeProjectVisibilityCommand,
    ChangeProjectVisibilityHandler,
)
from app.context.project.domain.exceptions.project_exceptions import ProjectNotFoundException
from app.context.project.domain.value_objects.project_visibility import ProjectVisibility
from tests.integration.project.conftest import (
    _AlwaysAllowProjectPermissionChecker,
    _NoopEventBus,
)


@pytest.mark.integration
class TestChangeProjectVisibilityHandler:
    """Тесты ChangeProjectVisibilityHandler."""

    @pytest.fixture
    def handler(self, project_repo, permission_checker_stub, event_bus_stub) -> ChangeProjectVisibilityHandler:
        return ChangeProjectVisibilityHandler(
            project_repo=project_repo,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_change_visibility_success(self, handler, project_repo, make_project) -> None:
        project = await make_project()
        cmd = ChangeProjectVisibilityCommand(
            caller_id=str(Id.generate()),
            project_id=str(project.id),
            visibility="private",
        )
        await handler.handle(cmd)

        found = await project_repo.get_by_id(project.id)
        assert found is not None
        assert found.visibility == ProjectVisibility.PRIVATE

    async def test_change_visibility_not_found(self, handler) -> None:
        cmd = ChangeProjectVisibilityCommand(
            caller_id=str(Id.generate()),
            project_id=str(Id.generate()),
            visibility="private",
        )
        with pytest.raises(ProjectNotFoundException):
            await handler.handle(cmd)

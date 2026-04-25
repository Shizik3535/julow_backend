"""Интеграционные тесты DeleteProjectRoleHandler (реальные repos + реальные порты)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.commands.delete_project_role import (
    DeleteProjectRoleCommand,
    DeleteProjectRoleHandler,
)
from app.context.project.domain.exceptions.project_role_exceptions import ProjectRoleNotFoundException
from tests.integration.project.conftest import (
    _AlwaysAllowProjectPermissionChecker,
    _NoopEventBus,
)


@pytest.mark.integration
class TestDeleteProjectRoleHandler:
    """Тесты DeleteProjectRoleHandler."""

    @pytest.fixture
    def handler(self, role_repo, permission_checker_stub, event_bus_stub) -> DeleteProjectRoleHandler:
        return DeleteProjectRoleHandler(
            role_repo=role_repo,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_delete_role_success(self, handler, role_repo, make_project_role) -> None:
        role = await make_project_role()
        cmd = DeleteProjectRoleCommand(
            caller_id=str(Id.generate()),
            project_id=str(role.project_id) if role.project_id else str(Id.generate()),
            role_id=str(role.id),
        )
        await handler.handle(cmd)

    async def test_delete_role_not_found(self, handler) -> None:
        cmd = DeleteProjectRoleCommand(
            caller_id=str(Id.generate()),
            project_id=str(Id.generate()),
            role_id=str(Id.generate()),
        )
        with pytest.raises(ProjectRoleNotFoundException):
            await handler.handle(cmd)

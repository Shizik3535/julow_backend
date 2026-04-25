"""Интеграционные тесты UpdateProjectRoleHandler (реальные repos + реальные порты)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.commands.update_project_role import (
    UpdateProjectRoleCommand,
    UpdateProjectRoleHandler,
)
from tests.integration.project.conftest import (
    _AlwaysAllowProjectPermissionChecker,
    _NoopEventBus,
)


@pytest.mark.integration
class TestUpdateProjectRoleHandler:
    """Тесты UpdateProjectRoleHandler."""

    @pytest.fixture
    def handler(self, role_repo, permission_checker_stub, event_bus_stub) -> UpdateProjectRoleHandler:
        return UpdateProjectRoleHandler(
            role_repo=role_repo,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_update_role_permissions(self, handler, role_repo, make_project_role) -> None:
        role = await make_project_role(permissions=["content.read"])
        cmd = UpdateProjectRoleCommand(
            caller_id=str(Id.generate()),
            project_id=str(role.project_id) if role.project_id else str(Id.generate()),
            role_id=str(role.id),
            permissions=["content.read", "content.write", "tasks.*"],
        )
        await handler.handle(cmd)

        found = await role_repo.get_by_id(role.id)
        assert found is not None
        assert "tasks.*" in found.permissions

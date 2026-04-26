"""Интеграционные тесты DeleteWorkspaceRoleHandler."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.commands.delete_workspace_role import (
    DeleteWorkspaceRoleCommand,
    DeleteWorkspaceRoleHandler,
)
from app.context.workspace.application.exceptions.authorization_exceptions import (
    InsufficientWorkspacePermissionsException,
)
from app.context.workspace.domain.exceptions.workspace_role_exceptions import WorkspaceRoleNotFoundException
from tests.integration.workspace.conftest import _AlwaysAllowPermissionChecker, _NoopEventBus


@pytest.mark.integration
class TestDeleteWorkspaceRoleHandler:
    """Тесты DeleteWorkspaceRoleHandler."""

    @pytest.fixture
    def handler(self, ws_role_repo) -> DeleteWorkspaceRoleHandler:
        return DeleteWorkspaceRoleHandler(
            role_repo=ws_role_repo,
            permission_checker=_AlwaysAllowPermissionChecker(),
            event_bus=_NoopEventBus(),
        )

    async def test_delete_custom_role_success(self, handler, ws_role_repo, make_workspace_role) -> None:
        role = await make_workspace_role()
        cmd = DeleteWorkspaceRoleCommand(
            caller_id=str(Id.generate()),
            role_id=str(role.id),
        )
        await handler.handle(cmd)

        found = await ws_role_repo.get_by_id(role.id)
        assert found is None

    async def test_delete_system_role_raises(self, ws_role_repo) -> None:
        from app.context.workspace.domain.aggregates.workspace_role import WorkspaceRole

        role = WorkspaceRole.create_system(name="sys-delete", permissions=["ws.*"])
        role.clear_domain_events()
        await ws_role_repo.add(role)

        handler = DeleteWorkspaceRoleHandler(
            role_repo=ws_role_repo,
            permission_checker=_AlwaysAllowPermissionChecker(),
            event_bus=_NoopEventBus(),
        )
        cmd = DeleteWorkspaceRoleCommand(
            caller_id=str(Id.generate()),
            role_id=str(role.id),
        )
        with pytest.raises(InsufficientWorkspacePermissionsException):
            await handler.handle(cmd)

    async def test_delete_role_not_found(self, handler) -> None:
        cmd = DeleteWorkspaceRoleCommand(
            caller_id=str(Id.generate()),
            role_id=str(Id.generate()),
        )
        with pytest.raises(WorkspaceRoleNotFoundException):
            await handler.handle(cmd)

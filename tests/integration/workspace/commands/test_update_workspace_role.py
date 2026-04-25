"""Интеграционные тесты UpdateWorkspaceRoleHandler."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.commands.update_workspace_role import (
    UpdateWorkspaceRoleCommand,
    UpdateWorkspaceRoleHandler,
)
from app.context.workspace.application.exceptions.authorization_exceptions import (
    InsufficientWorkspacePermissionsException,
)
from app.context.workspace.domain.exceptions.workspace_role_exceptions import WorkspaceRoleNotFoundException
from tests.integration.workspace.conftest import _AlwaysAllowPermissionChecker, _NoopEventBus


@pytest.mark.integration
class TestUpdateWorkspaceRoleHandler:
    """Тесты UpdateWorkspaceRoleHandler."""

    @pytest.fixture
    def handler(self, ws_role_repo) -> UpdateWorkspaceRoleHandler:
        return UpdateWorkspaceRoleHandler(
            role_repo=ws_role_repo,
            permission_checker=_AlwaysAllowPermissionChecker(),
            event_bus=_NoopEventBus(),
        )

    async def test_update_permissions(self, handler, ws_role_repo, make_workspace_role) -> None:
        role = await make_workspace_role()
        cmd = UpdateWorkspaceRoleCommand(
            caller_id=str(Id.generate()),
            role_id=str(role.id),
            permissions=["members.read", "members.write", "teams.read"],
        )
        await handler.handle(cmd)

        found = await ws_role_repo.get_by_id(role.id)
        assert found is not None
        assert found.permissions == ["members.read", "members.write", "teams.read"]

    async def test_update_description(self, handler, ws_role_repo, make_workspace_role) -> None:
        role = await make_workspace_role()
        cmd = UpdateWorkspaceRoleCommand(
            caller_id=str(Id.generate()),
            role_id=str(role.id),
            description="Updated description",
        )
        await handler.handle(cmd)

        found = await ws_role_repo.get_by_id(role.id)
        assert found is not None
        assert found.description == "Updated description"

    async def test_update_system_role_raises(self, ws_role_repo) -> None:
        from app.context.workspace.domain.aggregates.workspace_role import WorkspaceRole

        role = WorkspaceRole.create_system(name="sys-update", permissions=["ws.*"])
        role.clear_domain_events()
        await ws_role_repo.add(role)

        handler = UpdateWorkspaceRoleHandler(
            role_repo=ws_role_repo,
            permission_checker=_AlwaysAllowPermissionChecker(),
            event_bus=_NoopEventBus(),
        )
        cmd = UpdateWorkspaceRoleCommand(
            caller_id=str(Id.generate()),
            role_id=str(role.id),
            permissions=["new.perm"],
        )
        with pytest.raises(InsufficientWorkspacePermissionsException):
            await handler.handle(cmd)

    async def test_update_role_not_found(self, handler) -> None:
        cmd = UpdateWorkspaceRoleCommand(
            caller_id=str(Id.generate()),
            role_id=str(Id.generate()),
            permissions=["x"],
        )
        with pytest.raises(WorkspaceRoleNotFoundException):
            await handler.handle(cmd)

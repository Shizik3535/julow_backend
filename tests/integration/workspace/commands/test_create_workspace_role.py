"""Интеграционные тесты CreateWorkspaceRoleHandler."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.commands.create_workspace_role import (
    CreateWorkspaceRoleCommand,
    CreateWorkspaceRoleHandler,
)
from tests.integration.workspace.conftest import _AlwaysAllowPermissionChecker, _NoopEventBus


@pytest.mark.integration
class TestCreateWorkspaceRoleHandler:
    """Тесты CreateWorkspaceRoleHandler."""

    @pytest.fixture
    def handler(self, ws_role_repo) -> CreateWorkspaceRoleHandler:
        return CreateWorkspaceRoleHandler(
            role_repo=ws_role_repo,
            permission_checker=_AlwaysAllowPermissionChecker(),
            event_bus=_NoopEventBus(),
        )

    async def test_create_role_success(self, handler, ws_role_repo, make_workspace) -> None:
        ws = await make_workspace()
        cmd = CreateWorkspaceRoleCommand(
            caller_id=str(ws.owner_ids[0]),
            workspace_id=str(ws.id),
            name="editor",
            permissions=["members.read", "members.write"],
            description="Editor role",
        )
        result = await handler.handle(cmd)

        assert result.name == "editor"
        assert result.permissions == ["members.read", "members.write"]
        assert result.workspace_id == str(ws.id)

        role = await ws_role_repo.get_by_id(Id.from_string(result.id))
        assert role is not None

"""Интеграционные тесты AddWorkspaceOwnerHandler."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.commands.add_workspace_owner import (
    AddWorkspaceOwnerCommand,
    AddWorkspaceOwnerHandler,
)
from app.context.workspace.domain.exceptions.workspace_exceptions import WorkspaceNotFoundException
from tests.integration.workspace.conftest import _AlwaysAllowPermissionChecker, _NoopEventBus


@pytest.mark.integration
class TestAddWorkspaceOwnerHandler:
    """Тесты AddWorkspaceOwnerHandler."""

    @pytest.fixture
    def handler(self, ws_repo) -> AddWorkspaceOwnerHandler:
        return AddWorkspaceOwnerHandler(
            ws_repo=ws_repo,
            permission_checker=_AlwaysAllowPermissionChecker(),
            event_bus=_NoopEventBus(),
        )

    async def test_add_owner_success(self, handler, ws_repo, make_workspace) -> None:
        ws = await make_workspace()
        new_owner = Id.generate()

        cmd = AddWorkspaceOwnerCommand(
            caller_id=str(ws.owner_ids[0]),
            workspace_id=str(ws.id),
            user_id=str(new_owner),
        )
        await handler.handle(cmd)

        found = await ws_repo.get_by_id(ws.id)
        assert found is not None
        assert new_owner in found.owner_ids

    async def test_add_owner_not_found(self, handler) -> None:
        cmd = AddWorkspaceOwnerCommand(
            caller_id=str(Id.generate()),
            workspace_id=str(Id.generate()),
            user_id=str(Id.generate()),
        )
        with pytest.raises(WorkspaceNotFoundException):
            await handler.handle(cmd)

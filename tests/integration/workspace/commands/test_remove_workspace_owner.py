"""Интеграционные тесты RemoveWorkspaceOwnerHandler."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.commands.remove_workspace_owner import (
    RemoveWorkspaceOwnerCommand,
    RemoveWorkspaceOwnerHandler,
)
from app.context.workspace.domain.exceptions.workspace_exceptions import WorkspaceNotFoundException
from tests.integration.workspace.conftest import _AlwaysAllowPermissionChecker, _NoopEventBus


@pytest.mark.integration
class TestRemoveWorkspaceOwnerHandler:
    """Тесты RemoveWorkspaceOwnerHandler."""

    @pytest.fixture
    def handler(self, ws_repo) -> RemoveWorkspaceOwnerHandler:
        return RemoveWorkspaceOwnerHandler(
            ws_repo=ws_repo,
            permission_checker=_AlwaysAllowPermissionChecker(),
            event_bus=_NoopEventBus(),
        )

    async def test_remove_owner_success(self, handler, ws_repo, make_workspace) -> None:
        ws = await make_workspace()
        co_owner = Id.generate()
        ws.add_owner(co_owner)
        ws.clear_domain_events()
        await ws_repo.update(ws)

        cmd = RemoveWorkspaceOwnerCommand(
            caller_id=str(ws.owner_ids[0]),
            workspace_id=str(ws.id),
            user_id=str(co_owner),
        )
        await handler.handle(cmd)

        found = await ws_repo.get_by_id(ws.id)
        assert found is not None
        assert co_owner not in found.owner_ids

    async def test_remove_owner_not_found(self, handler) -> None:
        cmd = RemoveWorkspaceOwnerCommand(
            caller_id=str(Id.generate()),
            workspace_id=str(Id.generate()),
            user_id=str(Id.generate()),
        )
        with pytest.raises(WorkspaceNotFoundException):
            await handler.handle(cmd)

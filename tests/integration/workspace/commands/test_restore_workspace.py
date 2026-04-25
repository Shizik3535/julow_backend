"""Интеграционные тесты RestoreWorkspaceHandler."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.commands.restore_workspace import (
    RestoreWorkspaceCommand,
    RestoreWorkspaceHandler,
)
from app.context.workspace.domain.exceptions.workspace_exceptions import WorkspaceNotFoundException
from app.context.workspace.domain.value_objects.workspace_status import WorkspaceStatus
from tests.integration.workspace.conftest import _AlwaysAllowPermissionChecker, _NoopEventBus


@pytest.mark.integration
class TestRestoreWorkspaceHandler:
    """Тесты RestoreWorkspaceHandler."""

    @pytest.fixture
    def handler(self, ws_repo) -> RestoreWorkspaceHandler:
        return RestoreWorkspaceHandler(
            ws_repo=ws_repo,
            permission_checker=_AlwaysAllowPermissionChecker(),
            event_bus=_NoopEventBus(),
        )

    async def test_restore_success(self, handler, ws_repo, make_workspace) -> None:
        ws = await make_workspace()
        ws.archive()
        ws.clear_domain_events()
        await ws_repo.update(ws)

        cmd = RestoreWorkspaceCommand(
            caller_id=str(ws.owner_ids[0]),
            workspace_id=str(ws.id),
        )
        await handler.handle(cmd)

        found = await ws_repo.get_by_id(ws.id)
        assert found is not None
        assert found.status == WorkspaceStatus.ACTIVE

    async def test_restore_not_found(self, handler) -> None:
        cmd = RestoreWorkspaceCommand(
            caller_id=str(Id.generate()),
            workspace_id=str(Id.generate()),
        )
        with pytest.raises(WorkspaceNotFoundException):
            await handler.handle(cmd)

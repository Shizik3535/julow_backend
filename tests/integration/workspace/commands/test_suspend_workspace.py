"""Интеграционные тесты SuspendWorkspaceHandler."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.commands.suspend_workspace import (
    SuspendWorkspaceCommand,
    SuspendWorkspaceHandler,
)
from app.context.workspace.domain.exceptions.workspace_exceptions import WorkspaceNotFoundException
from app.context.workspace.domain.value_objects.workspace_status import WorkspaceStatus
from tests.integration.workspace.conftest import _AlwaysAllowPermissionChecker, _NoopEventBus


@pytest.mark.integration
class TestSuspendWorkspaceHandler:
    """Тесты SuspendWorkspaceHandler."""

    @pytest.fixture
    def handler(self, ws_repo) -> SuspendWorkspaceHandler:
        return SuspendWorkspaceHandler(
            ws_repo=ws_repo,
            permission_checker=_AlwaysAllowPermissionChecker(),
            event_bus=_NoopEventBus(),
        )

    async def test_suspend_success(self, handler, ws_repo, make_workspace) -> None:
        ws = await make_workspace()
        cmd = SuspendWorkspaceCommand(
            caller_id=str(ws.owner_ids[0]),
            workspace_id=str(ws.id),
            reason="Violation",
        )
        await handler.handle(cmd)

        found = await ws_repo.get_by_id(ws.id)
        assert found is not None
        assert found.status == WorkspaceStatus.SUSPENDED

    async def test_suspend_not_found(self, handler) -> None:
        cmd = SuspendWorkspaceCommand(
            caller_id=str(Id.generate()),
            workspace_id=str(Id.generate()),
            reason="test",
        )
        with pytest.raises(WorkspaceNotFoundException):
            await handler.handle(cmd)

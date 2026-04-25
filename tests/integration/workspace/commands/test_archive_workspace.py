"""Интеграционные тесты ArchiveWorkspaceHandler."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.commands.archive_workspace import (
    ArchiveWorkspaceCommand,
    ArchiveWorkspaceHandler,
)
from app.context.workspace.domain.exceptions.workspace_exceptions import (
    CannotArchiveWithChildrenException,
    WorkspaceNotFoundException,
)
from app.context.workspace.domain.value_objects.workspace_status import WorkspaceStatus
from tests.integration.workspace.conftest import _AlwaysAllowPermissionChecker, _NoopEventBus


@pytest.mark.integration
class TestArchiveWorkspaceHandler:
    """Тесты ArchiveWorkspaceHandler."""

    @pytest.fixture
    def handler(self, ws_repo) -> ArchiveWorkspaceHandler:
        return ArchiveWorkspaceHandler(
            ws_repo=ws_repo,
            permission_checker=_AlwaysAllowPermissionChecker(),
            event_bus=_NoopEventBus(),
        )

    async def test_archive_success(self, handler, ws_repo, make_workspace) -> None:
        ws = await make_workspace()
        cmd = ArchiveWorkspaceCommand(
            caller_id=str(ws.owner_ids[0]),
            workspace_id=str(ws.id),
        )
        await handler.handle(cmd)

        found = await ws_repo.get_by_id(ws.id)
        assert found is not None
        assert found.status == WorkspaceStatus.ARCHIVED

    async def test_archive_with_active_children_raises(
        self, handler, make_workspace
    ) -> None:
        parent = await make_workspace()
        await make_workspace(parent_workspace_id=parent.id)

        cmd = ArchiveWorkspaceCommand(
            caller_id=str(parent.owner_ids[0]),
            workspace_id=str(parent.id),
        )
        with pytest.raises(CannotArchiveWithChildrenException):
            await handler.handle(cmd)

    async def test_archive_not_found(self, handler) -> None:
        cmd = ArchiveWorkspaceCommand(
            caller_id=str(Id.generate()),
            workspace_id=str(Id.generate()),
        )
        with pytest.raises(WorkspaceNotFoundException):
            await handler.handle(cmd)

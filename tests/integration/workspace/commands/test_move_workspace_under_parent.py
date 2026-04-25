"""Интеграционные тесты MoveWorkspaceUnderParentHandler."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.commands.move_workspace_under_parent import (
    MoveWorkspaceUnderParentCommand,
    MoveWorkspaceUnderParentHandler,
)
from app.context.workspace.domain.exceptions.workspace_exceptions import (
    CircularWorkspaceHierarchyException,
    ParentWorkspaceNotFoundException,
    WorkspaceNotFoundException,
)
from tests.integration.workspace.conftest import _AlwaysAllowPermissionChecker, _NoopEventBus


@pytest.mark.integration
class TestMoveWorkspaceUnderParentHandler:
    """Тесты MoveWorkspaceUnderParentHandler."""

    @pytest.fixture
    def handler(self, ws_repo) -> MoveWorkspaceUnderParentHandler:
        return MoveWorkspaceUnderParentHandler(
            ws_repo=ws_repo,
            permission_checker=_AlwaysAllowPermissionChecker(),
            event_bus=_NoopEventBus(),
        )

    async def test_move_under_parent_success(self, handler, ws_repo, make_workspace) -> None:
        parent = await make_workspace()
        child = await make_workspace()

        cmd = MoveWorkspaceUnderParentCommand(
            caller_id=str(child.owner_ids[0]),
            workspace_id=str(child.id),
            parent_workspace_id=str(parent.id),
        )
        await handler.handle(cmd)

        found = await ws_repo.get_by_id(child.id)
        assert found is not None
        assert found.parent_workspace_id == parent.id

    async def test_detach_from_parent(self, handler, ws_repo, make_workspace) -> None:
        parent = await make_workspace()
        child = await make_workspace(parent_workspace_id=parent.id)

        cmd = MoveWorkspaceUnderParentCommand(
            caller_id=str(child.owner_ids[0]),
            workspace_id=str(child.id),
            parent_workspace_id=None,
        )
        await handler.handle(cmd)

        found = await ws_repo.get_by_id(child.id)
        assert found is not None
        assert found.parent_workspace_id is None

    async def test_parent_not_found(self, handler, make_workspace) -> None:
        child = await make_workspace()

        cmd = MoveWorkspaceUnderParentCommand(
            caller_id=str(child.owner_ids[0]),
            workspace_id=str(child.id),
            parent_workspace_id=str(Id.generate()),
        )
        with pytest.raises(ParentWorkspaceNotFoundException):
            await handler.handle(cmd)

    async def test_workspace_not_found(self, handler) -> None:
        cmd = MoveWorkspaceUnderParentCommand(
            caller_id=str(Id.generate()),
            workspace_id=str(Id.generate()),
            parent_workspace_id=str(Id.generate()),
        )
        with pytest.raises(WorkspaceNotFoundException):
            await handler.handle(cmd)

    async def test_circular_hierarchy_raises(self, handler, make_workspace) -> None:
        parent = await make_workspace()
        child = await make_workspace(parent_workspace_id=parent.id)

        cmd = MoveWorkspaceUnderParentCommand(
            caller_id=str(parent.owner_ids[0]),
            workspace_id=str(parent.id),
            parent_workspace_id=str(child.id),
        )
        with pytest.raises(CircularWorkspaceHierarchyException):
            await handler.handle(cmd)

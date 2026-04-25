"""Интеграционные тесты TransferWorkspaceOwnershipHandler."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.commands.transfer_workspace_ownership import (
    TransferWorkspaceOwnershipCommand,
    TransferWorkspaceOwnershipHandler,
)
from app.context.workspace.domain.exceptions.workspace_exceptions import WorkspaceNotFoundException
from tests.integration.workspace.conftest import _AlwaysAllowPermissionChecker, _NoopEventBus


@pytest.mark.integration
class TestTransferWorkspaceOwnershipHandler:
    """Тесты TransferWorkspaceOwnershipHandler."""

    @pytest.fixture
    def handler(self, ws_repo) -> TransferWorkspaceOwnershipHandler:
        return TransferWorkspaceOwnershipHandler(
            ws_repo=ws_repo,
            permission_checker=_AlwaysAllowPermissionChecker(),
            event_bus=_NoopEventBus(),
        )

    async def test_transfer_success(self, handler, ws_repo, make_workspace) -> None:
        ws = await make_workspace()
        new_owner = Id.generate()

        cmd = TransferWorkspaceOwnershipCommand(
            caller_id=str(ws.owner_ids[0]),
            workspace_id=str(ws.id),
            from_id=str(ws.owner_ids[0]),
            to_id=str(new_owner),
        )
        await handler.handle(cmd)

        found = await ws_repo.get_by_id(ws.id)
        assert found is not None
        assert new_owner in found.owner_ids

    async def test_transfer_not_found(self, handler) -> None:
        cmd = TransferWorkspaceOwnershipCommand(
            caller_id=str(Id.generate()),
            workspace_id=str(Id.generate()),
            from_id=str(Id.generate()),
            to_id=str(Id.generate()),
        )
        with pytest.raises(WorkspaceNotFoundException):
            await handler.handle(cmd)

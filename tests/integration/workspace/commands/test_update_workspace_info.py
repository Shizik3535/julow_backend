"""Интеграционные тесты UpdateWorkspaceInfoHandler."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.commands.update_workspace_info import (
    UpdateWorkspaceInfoCommand,
    UpdateWorkspaceInfoHandler,
)
from app.context.workspace.domain.exceptions.workspace_exceptions import WorkspaceNotFoundException
from tests.integration.workspace.conftest import _AlwaysAllowPermissionChecker, _NoopEventBus


@pytest.mark.integration
class TestUpdateWorkspaceInfoHandler:
    """Тесты UpdateWorkspaceInfoHandler."""

    @pytest.fixture
    def handler(self, ws_repo) -> UpdateWorkspaceInfoHandler:
        return UpdateWorkspaceInfoHandler(
            ws_repo=ws_repo,
            permission_checker=_AlwaysAllowPermissionChecker(),
            event_bus=_NoopEventBus(),
        )

    async def test_update_name(self, handler, ws_repo, make_workspace) -> None:
        ws = await make_workspace()
        cmd = UpdateWorkspaceInfoCommand(
            caller_id=str(ws.owner_ids[0]),
            workspace_id=str(ws.id),
            name="Updated Name",
        )
        await handler.handle(cmd)

        found = await ws_repo.get_by_id(ws.id)
        assert found is not None
        assert found.name == "Updated Name"

    async def test_update_with_color(self, handler, ws_repo, make_workspace) -> None:
        ws = await make_workspace()
        cmd = UpdateWorkspaceInfoCommand(
            caller_id=str(ws.owner_ids[0]),
            workspace_id=str(ws.id),
            color="#FF5500",
        )
        await handler.handle(cmd)

        found = await ws_repo.get_by_id(ws.id)
        assert found is not None
        assert str(found.personalization.color) == "#FF5500"

    async def test_update_with_description(self, handler, ws_repo, make_workspace) -> None:
        ws = await make_workspace()
        cmd = UpdateWorkspaceInfoCommand(
            caller_id=str(ws.owner_ids[0]),
            workspace_id=str(ws.id),
            description="New description",
        )
        await handler.handle(cmd)

        found = await ws_repo.get_by_id(ws.id)
        assert found is not None
        assert found.personalization.description == "New description"

    async def test_update_workspace_not_found(self, handler) -> None:
        cmd = UpdateWorkspaceInfoCommand(
            caller_id=str(Id.generate()),
            workspace_id=str(Id.generate()),
            name="Nope",
        )
        with pytest.raises(WorkspaceNotFoundException):
            await handler.handle(cmd)

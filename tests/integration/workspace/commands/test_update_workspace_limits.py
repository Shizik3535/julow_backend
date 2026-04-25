"""Интеграционные тесты UpdateWorkspaceLimitsHandler."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.commands.update_workspace_limits import (
    UpdateWorkspaceLimitsCommand,
    UpdateWorkspaceLimitsHandler,
)
from app.context.workspace.domain.exceptions.workspace_exceptions import WorkspaceNotFoundException
from tests.integration.workspace.conftest import _AlwaysAllowPermissionChecker, _NoopEventBus


@pytest.mark.integration
class TestUpdateWorkspaceLimitsHandler:
    """Тесты UpdateWorkspaceLimitsHandler."""

    @pytest.fixture
    def handler(self, ws_repo) -> UpdateWorkspaceLimitsHandler:
        return UpdateWorkspaceLimitsHandler(
            ws_repo=ws_repo,
            permission_checker=_AlwaysAllowPermissionChecker(),
            event_bus=_NoopEventBus(),
        )

    async def test_update_limits_success(self, handler, ws_repo, make_workspace) -> None:
        ws = await make_workspace()
        cmd = UpdateWorkspaceLimitsCommand(
            caller_id=str(ws.owner_ids[0]),
            workspace_id=str(ws.id),
            max_members=100,
            max_projects=50,
        )
        await handler.handle(cmd)

        found = await ws_repo.get_by_id(ws.id)
        assert found is not None
        assert found.limits.max_members == 100
        assert found.limits.max_projects == 50

    async def test_update_limits_not_found(self, handler) -> None:
        cmd = UpdateWorkspaceLimitsCommand(
            caller_id=str(Id.generate()),
            workspace_id=str(Id.generate()),
            max_members=10,
        )
        with pytest.raises(WorkspaceNotFoundException):
            await handler.handle(cmd)

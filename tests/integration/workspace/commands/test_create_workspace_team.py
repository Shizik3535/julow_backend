"""Интеграционные тесты CreateWorkspaceTeamHandler."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.commands.create_workspace_team import (
    CreateWorkspaceTeamCommand,
    CreateWorkspaceTeamHandler,
)
from tests.integration.workspace.conftest import _AlwaysAllowPermissionChecker, _NoopEventBus


@pytest.mark.integration
class TestCreateWorkspaceTeamHandler:
    """Тесты CreateWorkspaceTeamHandler."""

    @pytest.fixture
    def handler(self, ws_team_repo) -> CreateWorkspaceTeamHandler:
        return CreateWorkspaceTeamHandler(
            team_repo=ws_team_repo,
            permission_checker=_AlwaysAllowPermissionChecker(),
            event_bus=_NoopEventBus(),
        )

    async def test_create_team_success(self, handler, ws_team_repo, make_workspace) -> None:
        ws = await make_workspace()
        cmd = CreateWorkspaceTeamCommand(
            caller_id=str(ws.owner_ids[0]),
            workspace_id=str(ws.id),
            name="Dev Team",
        )
        result = await handler.handle(cmd)

        assert result.name == "Dev Team"
        assert result.workspace_id == str(ws.id)

        team = await ws_team_repo.get_by_id(Id.from_string(result.id))
        assert team is not None

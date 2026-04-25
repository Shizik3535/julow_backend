"""Интеграционные тесты DeactivateWorkspaceTeamHandler."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.commands.deactivate_workspace_team import (
    DeactivateWorkspaceTeamCommand,
    DeactivateWorkspaceTeamHandler,
)
from app.context.workspace.domain.exceptions.workspace_team_exceptions import WorkspaceTeamNotFoundException
from tests.integration.workspace.conftest import _AlwaysAllowPermissionChecker, _NoopEventBus


@pytest.mark.integration
class TestDeactivateWorkspaceTeamHandler:
    """Тесты DeactivateWorkspaceTeamHandler."""

    @pytest.fixture
    def handler(self, ws_team_repo) -> DeactivateWorkspaceTeamHandler:
        return DeactivateWorkspaceTeamHandler(
            team_repo=ws_team_repo,
            permission_checker=_AlwaysAllowPermissionChecker(),
            event_bus=_NoopEventBus(),
        )

    async def test_deactivate_success(self, handler, ws_team_repo, make_workspace_team) -> None:
        team = await make_workspace_team()
        cmd = DeactivateWorkspaceTeamCommand(
            caller_id=str(Id.generate()),
            team_id=str(team.id),
        )
        await handler.handle(cmd)

        found = await ws_team_repo.get_by_id(team.id)
        assert found is not None
        assert found.is_active is False

    async def test_team_not_found(self, handler) -> None:
        cmd = DeactivateWorkspaceTeamCommand(
            caller_id=str(Id.generate()),
            team_id=str(Id.generate()),
        )
        with pytest.raises(WorkspaceTeamNotFoundException):
            await handler.handle(cmd)

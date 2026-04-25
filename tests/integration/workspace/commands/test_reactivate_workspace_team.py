"""Интеграционные тесты ReactivateWorkspaceTeamHandler."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.commands.reactivate_workspace_team import (
    ReactivateWorkspaceTeamCommand,
    ReactivateWorkspaceTeamHandler,
)
from app.context.workspace.domain.exceptions.workspace_team_exceptions import WorkspaceTeamNotFoundException
from tests.integration.workspace.conftest import _AlwaysAllowPermissionChecker, _NoopEventBus


@pytest.mark.integration
class TestReactivateWorkspaceTeamHandler:
    """Тесты ReactivateWorkspaceTeamHandler."""

    @pytest.fixture
    def handler(self, ws_team_repo) -> ReactivateWorkspaceTeamHandler:
        return ReactivateWorkspaceTeamHandler(
            team_repo=ws_team_repo,
            permission_checker=_AlwaysAllowPermissionChecker(),
            event_bus=_NoopEventBus(),
        )

    async def test_reactivate_success(self, handler, ws_team_repo, make_workspace_team) -> None:
        team = await make_workspace_team()
        team.deactivate()
        team.clear_domain_events()
        await ws_team_repo.update(team)

        cmd = ReactivateWorkspaceTeamCommand(
            caller_id=str(Id.generate()),
            team_id=str(team.id),
        )
        await handler.handle(cmd)

        found = await ws_team_repo.get_by_id(team.id)
        assert found is not None
        assert found.is_active is True

    async def test_team_not_found(self, handler) -> None:
        cmd = ReactivateWorkspaceTeamCommand(
            caller_id=str(Id.generate()),
            team_id=str(Id.generate()),
        )
        with pytest.raises(WorkspaceTeamNotFoundException):
            await handler.handle(cmd)

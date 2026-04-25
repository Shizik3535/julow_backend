"""Интеграционные тесты UpdateWorkspaceTeamHandler."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.commands.update_workspace_team import (
    UpdateWorkspaceTeamCommand,
    UpdateWorkspaceTeamHandler,
)
from app.context.workspace.domain.exceptions.workspace_team_exceptions import WorkspaceTeamNotFoundException
from tests.integration.workspace.conftest import _AlwaysAllowPermissionChecker, _NoopEventBus


@pytest.mark.integration
class TestUpdateWorkspaceTeamHandler:
    """Тесты UpdateWorkspaceTeamHandler."""

    @pytest.fixture
    def handler(self, ws_team_repo) -> UpdateWorkspaceTeamHandler:
        return UpdateWorkspaceTeamHandler(
            team_repo=ws_team_repo,
            permission_checker=_AlwaysAllowPermissionChecker(),
            event_bus=_NoopEventBus(),
        )

    async def test_update_name(self, handler, ws_team_repo, make_workspace_team) -> None:
        team = await make_workspace_team()
        cmd = UpdateWorkspaceTeamCommand(
            caller_id=str(Id.generate()),
            team_id=str(team.id),
            name="Updated Team",
        )
        await handler.handle(cmd)

        found = await ws_team_repo.get_by_id(team.id)
        assert found is not None
        assert found.name == "Updated Team"

    async def test_update_description(self, handler, ws_team_repo, make_workspace_team) -> None:
        team = await make_workspace_team()
        cmd = UpdateWorkspaceTeamCommand(
            caller_id=str(Id.generate()),
            team_id=str(team.id),
            description="New desc",
        )
        await handler.handle(cmd)

        found = await ws_team_repo.get_by_id(team.id)
        assert found is not None
        assert found.description == "New desc"

    async def test_update_lead(self, handler, ws_team_repo, make_workspace_team) -> None:
        team = await make_workspace_team()
        new_lead = Id.generate()
        cmd = UpdateWorkspaceTeamCommand(
            caller_id=str(Id.generate()),
            team_id=str(team.id),
            lead_id=str(new_lead),
        )
        await handler.handle(cmd)

        found = await ws_team_repo.get_by_id(team.id)
        assert found is not None
        assert found.lead_id == new_lead

    async def test_team_not_found(self, handler) -> None:
        cmd = UpdateWorkspaceTeamCommand(
            caller_id=str(Id.generate()),
            team_id=str(Id.generate()),
            name="Nope",
        )
        with pytest.raises(WorkspaceTeamNotFoundException):
            await handler.handle(cmd)

"""Интеграционные тесты UpdateTeamHandler (реальные repos + stubs)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.commands.update_team import (
    UpdateTeamCommand,
    UpdateTeamHandler,
)


@pytest.mark.integration
class TestUpdateTeamHandler:
    @pytest.fixture
    def handler(self, team_repo, permission_checker_stub, event_bus_stub):
        return UpdateTeamHandler(
            team_repo=team_repo,
            org_permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_update_name(self, handler, make_team, team_repo) -> None:
        team = await make_team()
        cmd = UpdateTeamCommand(
            caller_id=str(Id.generate()),
            org_id=str(team.org_id),
            team_id=str(team.id),
            name="UpdatedTeam",
        )
        await handler.handle(cmd)
        found = await team_repo.get_by_id(team.id)
        assert found is not None
        assert found.name == "UpdatedTeam"

    async def test_update_description_and_lead(self, handler, make_team, team_repo) -> None:
        new_lead = Id.generate()
        team = await make_team()
        cmd = UpdateTeamCommand(
            caller_id=str(Id.generate()),
            org_id=str(team.org_id),
            team_id=str(team.id),
            description="New desc",
            lead_id=str(new_lead),
        )
        await handler.handle(cmd)
        found = await team_repo.get_by_id(team.id)
        assert found is not None
        assert found.description == "New desc"
        assert found.lead_id == new_lead

"""Интеграционные тесты ReactivateTeamHandler (реальные repos + stubs)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.commands.reactivate_team import (
    ReactivateTeamCommand,
    ReactivateTeamHandler,
)


@pytest.mark.integration
class TestReactivateTeamHandler:
    @pytest.fixture
    def handler(self, team_repo, permission_checker_stub, event_bus_stub):
        return ReactivateTeamHandler(
            team_repo=team_repo,
            org_permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_reactivate(self, handler, make_team, team_repo) -> None:
        team = await make_team()
        team.deactivate()
        team.clear_domain_events()
        await team_repo.update(team)

        cmd = ReactivateTeamCommand(
            caller_id=str(Id.generate()),
            org_id=str(team.org_id),
            team_id=str(team.id),
        )
        await handler.handle(cmd)
        found = await team_repo.get_by_id(team.id)
        assert found is not None
        assert found.is_active is True

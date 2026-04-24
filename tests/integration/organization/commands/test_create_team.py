"""Интеграционные тесты CreateTeamHandler (реальные repos + stubs)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.commands.create_team import (
    CreateTeamCommand,
    CreateTeamHandler,
)
from app.context.organization.application.dto.team_dto import TeamDTO


@pytest.mark.integration
class TestCreateTeamHandler:
    @pytest.fixture
    def handler(self, team_repo, permission_checker_stub, event_bus_stub):
        return CreateTeamHandler(
            team_repo=team_repo,
            org_permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_create_team(self, handler, make_org) -> None:
        org = await make_org()
        cmd = CreateTeamCommand(
            caller_id=str(Id.generate()),
            org_id=str(org.id),
            name="Alpha",
        )
        result = await handler.handle(cmd)
        assert isinstance(result, TeamDTO)
        assert result.name == "Alpha"

    async def test_create_with_lead(self, handler, make_org) -> None:
        org = await make_org()
        lead = Id.generate()
        cmd = CreateTeamCommand(
            caller_id=str(Id.generate()),
            org_id=str(org.id),
            name="Beta",
            lead_id=str(lead),
        )
        result = await handler.handle(cmd)
        assert result.lead_id == str(lead)

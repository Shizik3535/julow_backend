"""Интеграционные тесты GetTeamHandler (реальные repos)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.dto.team_dto import TeamDTO
from app.context.organization.application.queries.get_team import (
    GetTeamHandler,
    GetTeamQuery,
)
from app.context.organization.domain.exceptions.team_exceptions import TeamNotFoundException


@pytest.mark.integration
class TestGetTeamHandler:
    @pytest.fixture
    def handler(self, team_repo, permission_checker_stub) -> GetTeamHandler:
        return GetTeamHandler(team_repo=team_repo, org_permission_checker=permission_checker_stub)

    async def test_returns_team_dto(self, handler, make_team) -> None:
        team = await make_team(name="Alpha")
        query = GetTeamQuery(caller_id=str(Id.generate()), org_id=str(team.org_id), team_id=str(team.id))
        result = await handler.handle(query)
        assert isinstance(result, TeamDTO)
        assert result.name == "Alpha"

    async def test_not_found_raises(self, handler) -> None:
        query = GetTeamQuery(caller_id=str(Id.generate()), org_id=str(Id.generate()), team_id=str(Id.generate()))
        with pytest.raises(TeamNotFoundException):
            await handler.handle(query)

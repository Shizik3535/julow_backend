"""Интеграционные тесты GetTeamsByOrgHandler (реальные repos)."""

import pytest

from app.context.organization.application.dto.team_dto import TeamListDTO
from app.context.organization.application.queries.get_teams_by_org import (
    GetTeamsByOrgHandler,
    GetTeamsByOrgQuery,
)


@pytest.mark.integration
class TestGetTeamsByOrgHandler:
    @pytest.fixture
    def handler(self, team_repo) -> GetTeamsByOrgHandler:
        return GetTeamsByOrgHandler(team_repo=team_repo)

    async def test_returns_teams(self, handler, make_team, make_org) -> None:
        org = await make_org()
        team = await make_team(org_id=org.id)
        query = GetTeamsByOrgQuery(org_id=str(org.id))
        result = await handler.handle(query)
        assert isinstance(result, TeamListDTO)
        assert any(t.id == str(team.id) for t in result.items)

    async def test_empty_for_unknown_org(self, handler) -> None:
        from app.shared.domain.value_objects.id_vo import Id

        query = GetTeamsByOrgQuery(org_id=str(Id.generate()))
        result = await handler.handle(query)
        assert result.total == 0

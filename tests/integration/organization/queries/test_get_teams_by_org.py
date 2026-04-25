"""Интеграционные тесты GetTeamsByOrgHandler (реальные repos)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.dto.team_dto import TeamListDTO
from app.context.organization.application.queries.get_teams_by_org import (
    GetTeamsByOrgHandler,
    GetTeamsByOrgQuery,
)


@pytest.mark.integration
class TestGetTeamsByOrgHandler:
    @pytest.fixture
    def handler(self, team_repo, org_repo, permission_checker_stub) -> GetTeamsByOrgHandler:
        return GetTeamsByOrgHandler(team_repo=team_repo, org_repo=org_repo, org_permission_checker=permission_checker_stub)

    async def test_returns_teams(self, handler, make_team, make_org) -> None:
        org = await make_org()
        team = await make_team(org_id=org.id)
        query = GetTeamsByOrgQuery(caller_id=str(Id.generate()), org_id=str(org.id))
        result = await handler.handle(query)
        assert isinstance(result, TeamListDTO)
        assert any(t.id == str(team.id) for t in result.items)

    async def test_not_found_raises_for_unknown_org(self, handler) -> None:
        from app.context.organization.domain.exceptions.organization_exceptions import OrganizationNotFoundException

        query = GetTeamsByOrgQuery(caller_id=str(Id.generate()), org_id=str(Id.generate()))
        with pytest.raises(OrganizationNotFoundException):
            await handler.handle(query)

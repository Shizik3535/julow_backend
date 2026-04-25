"""Интеграционные тесты GetWorkspaceTeamHandler."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.queries.get_workspace_team import (
    GetWorkspaceTeamQuery,
    GetWorkspaceTeamHandler,
)
from app.context.workspace.domain.exceptions.workspace_team_exceptions import WorkspaceTeamNotFoundException
from tests.integration.workspace.conftest import _AlwaysAllowPermissionChecker


@pytest.mark.integration
class TestGetWorkspaceTeamHandler:
    """Тесты GetWorkspaceTeamHandler."""

    @pytest.fixture
    def handler(self, ws_team_repo) -> GetWorkspaceTeamHandler:
        return GetWorkspaceTeamHandler(
            team_repo=ws_team_repo,
            permission_checker=_AlwaysAllowPermissionChecker(),
        )

    async def test_get_team_found(self, handler, make_workspace_team) -> None:
        team = await make_workspace_team(name="Query Team")
        query = GetWorkspaceTeamQuery(caller_id=str(Id.generate()), team_id=str(team.id))
        result = await handler.handle(query)

        assert result.id == str(team.id)
        assert result.name == "Query Team"
        assert result.is_active is True

    async def test_get_team_not_found(self, handler) -> None:
        query = GetWorkspaceTeamQuery(caller_id=str(Id.generate()), team_id=str(Id.generate()))
        with pytest.raises(WorkspaceTeamNotFoundException):
            await handler.handle(query)

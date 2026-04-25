"""Интеграционные тесты GetWorkspaceTeamsHandler."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.queries.get_workspace_teams import (
    GetWorkspaceTeamsQuery,
    GetWorkspaceTeamsHandler,
)
from tests.integration.workspace.conftest import _AlwaysAllowPermissionChecker


@pytest.mark.integration
class TestGetWorkspaceTeamsHandler:
    """Тесты GetWorkspaceTeamsHandler."""

    @pytest.fixture
    def handler(self, ws_team_repo) -> GetWorkspaceTeamsHandler:
        return GetWorkspaceTeamsHandler(
            team_repo=ws_team_repo,
            permission_checker=_AlwaysAllowPermissionChecker(),
        )

    async def test_get_teams_found(self, handler, make_workspace_team) -> None:
        team = await make_workspace_team(name="List Team")
        query = GetWorkspaceTeamsQuery(
            caller_id=str(Id.generate()), workspace_id=str(team.workspace_id),
        )
        result = await handler.handle(query)

        assert result.total >= 1
        names = [t.name for t in result.items]
        assert "List Team" in names

    async def test_get_teams_empty(self, handler) -> None:
        query = GetWorkspaceTeamsQuery(
            caller_id=str(Id.generate()), workspace_id=str(Id.generate()),
        )
        result = await handler.handle(query)

        assert result.total == 0

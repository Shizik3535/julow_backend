"""Unit-тесты для исключений WorkspaceTeam aggregate (Workspace BC)."""

import pytest

from app.shared.domain.exceptions import EntityNotFoundException
from app.context.workspace.domain.exceptions.workspace_team_exceptions import (
    WorkspaceTeamNotFoundException,
)


@pytest.mark.unit
class TestWorkspaceTeamNotFoundException:
    def test_is_entity_not_found(self) -> None:
        exc = WorkspaceTeamNotFoundException(id="t1")
        assert isinstance(exc, EntityNotFoundException)
        assert exc.entity_type == "WorkspaceTeam"

    def test_message_contains_id(self) -> None:
        exc = WorkspaceTeamNotFoundException(id="t1")
        assert "t1" in exc.message

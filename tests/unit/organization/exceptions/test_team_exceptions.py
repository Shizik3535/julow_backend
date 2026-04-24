"""Unit-тесты для исключений Team aggregate (Organization BC)."""

import pytest

from app.shared.domain.exceptions import EntityNotFoundException
from app.context.organization.domain.exceptions.team_exceptions import (
    TeamNotFoundException,
)


@pytest.mark.unit
class TestTeamNotFoundException:
    def test_is_entity_not_found(self) -> None:
        exc = TeamNotFoundException(id="team-1")
        assert isinstance(exc, EntityNotFoundException)
        assert exc.entity_type == "Team"

    def test_message_contains_id(self) -> None:
        exc = TeamNotFoundException(id="team-1")
        assert "team-1" in exc.message

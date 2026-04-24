"""Unit-тесты для исключений Epic aggregate (Project BC)."""

import pytest

from app.shared.domain.exceptions import EntityNotFoundException
from app.context.project.domain.exceptions.epic_exceptions import EpicNotFoundException


@pytest.mark.unit
class TestEpicNotFoundException:
    def test_is_entity_not_found(self) -> None:
        exc = EpicNotFoundException(id="epic-1")
        assert isinstance(exc, EntityNotFoundException)
        assert exc.entity_type == "Epic"

    def test_message_contains_id(self) -> None:
        exc = EpicNotFoundException(id="epic-1")
        assert "epic-1" in exc.message

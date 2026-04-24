"""Unit-тесты для исключений ChangelogEntry aggregate (Task BC)."""

import pytest

from app.shared.domain.exceptions import EntityNotFoundException
from app.context.task.domain.exceptions.changelog_exceptions import ChangelogNotFoundException


@pytest.mark.unit
class TestChangelogNotFoundException:
    def test_is_entity_not_found(self) -> None:
        exc = ChangelogNotFoundException(id="cl-1")
        assert isinstance(exc, EntityNotFoundException)
        assert exc.entity_type == "ChangelogEntry"

    def test_message_contains_id(self) -> None:
        exc = ChangelogNotFoundException(id="cl-1")
        assert "cl-1" in exc.message

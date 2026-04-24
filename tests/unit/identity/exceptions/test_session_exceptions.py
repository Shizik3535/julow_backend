"""Unit-тесты для исключений Session aggregate (Identity BC)."""

import pytest

from app.shared.domain.base_exceptions import DomainException
from app.shared.domain.exceptions import EntityNotFoundException
from app.context.identity.domain.exceptions.session_exceptions import (
    SessionExpiredException,
    SessionNotFoundException,
    UnauthorizedSessionAccessException,
)


@pytest.mark.unit
class TestSessionNotFoundException:
    def test_is_entity_not_found(self) -> None:
        exc = SessionNotFoundException(id="abc-123")
        assert isinstance(exc, EntityNotFoundException)
        assert exc.entity_type == "Session"


@pytest.mark.unit
class TestSessionExpiredException:
    def test_is_domain(self) -> None:
        exc = SessionExpiredException()
        assert isinstance(exc, DomainException)


@pytest.mark.unit
class TestUnauthorizedSessionAccessException:
    def test_is_domain(self) -> None:
        exc = UnauthorizedSessionAccessException()
        assert isinstance(exc, DomainException)

"""Unit-тесты для исключений Project aggregate (Project BC)."""

import pytest

from app.shared.domain.base_exceptions import DomainException
from app.shared.domain.exceptions import BusinessRuleViolationException, EntityNotFoundException
from app.context.project.domain.exceptions.project_exceptions import (
    ProjectNotFoundException,
    ProjectSuspendedException,
    ProjectArchivedException,
    CannotChangeMethodologyWithActiveSprintsException,
    MethodologyCapabilityNotAvailableException,
)


@pytest.mark.unit
class TestProjectNotFoundException:
    def test_is_entity_not_found(self) -> None:
        exc = ProjectNotFoundException(id="abc-123")
        assert isinstance(exc, EntityNotFoundException)
        assert exc.entity_type == "Project"

    def test_message_contains_id(self) -> None:
        exc = ProjectNotFoundException(id="abc-123")
        assert "abc-123" in exc.message


@pytest.mark.unit
class TestProjectSuspendedException:
    def test_is_domain(self) -> None:
        exc = ProjectSuspendedException()
        assert isinstance(exc, DomainException)

    def test_message(self) -> None:
        exc = ProjectSuspendedException()
        assert "приостановлен" in exc.message.lower()


@pytest.mark.unit
class TestProjectArchivedException:
    def test_is_domain(self) -> None:
        exc = ProjectArchivedException()
        assert isinstance(exc, DomainException)

    def test_message(self) -> None:
        exc = ProjectArchivedException()
        assert "архивирован" in exc.message.lower()


@pytest.mark.unit
class TestCannotChangeMethodologyWithActiveSprintsException:
    def test_is_business_rule(self) -> None:
        exc = CannotChangeMethodologyWithActiveSprintsException()
        assert isinstance(exc, BusinessRuleViolationException)

    def test_rule(self) -> None:
        exc = CannotChangeMethodologyWithActiveSprintsException()
        assert exc.rule == "NoMethodologyChangeWithActiveSprints"


@pytest.mark.unit
class TestMethodologyCapabilityNotAvailableException:
    def test_is_business_rule(self) -> None:
        exc = MethodologyCapabilityNotAvailableException()
        assert isinstance(exc, BusinessRuleViolationException)

    def test_rule(self) -> None:
        exc = MethodologyCapabilityNotAvailableException()
        assert exc.rule == "MethodologyCapability"

    def test_message_with_capability(self) -> None:
        exc = MethodologyCapabilityNotAvailableException(capability="sprints")
        assert "sprints" in exc.message

    def test_message_without_capability(self) -> None:
        exc = MethodologyCapabilityNotAvailableException()
        assert "методологии" in exc.message.lower()

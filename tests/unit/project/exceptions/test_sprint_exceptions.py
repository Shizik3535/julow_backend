"""Unit-тесты для исключений Sprint aggregate (Project BC)."""

import pytest

from app.shared.domain.exceptions import BusinessRuleViolationException, EntityNotFoundException
from app.context.project.domain.exceptions.sprint_exceptions import (
    SprintNotFoundException,
    SprintAlreadyStartedException,
    SprintNotStartedException,
    CannotCompleteSprintWithOpenTasksException,
)


@pytest.mark.unit
class TestSprintNotFoundException:
    def test_is_entity_not_found(self) -> None:
        exc = SprintNotFoundException(id="sprint-1")
        assert isinstance(exc, EntityNotFoundException)
        assert exc.entity_type == "Sprint"

    def test_message_contains_id(self) -> None:
        exc = SprintNotFoundException(id="sprint-1")
        assert "sprint-1" in exc.message


@pytest.mark.unit
class TestSprintAlreadyStartedException:
    def test_is_business_rule(self) -> None:
        exc = SprintAlreadyStartedException()
        assert isinstance(exc, BusinessRuleViolationException)

    def test_rule(self) -> None:
        exc = SprintAlreadyStartedException()
        assert exc.rule == "SprintAlreadyStarted"


@pytest.mark.unit
class TestSprintNotStartedException:
    def test_is_business_rule(self) -> None:
        exc = SprintNotStartedException()
        assert isinstance(exc, BusinessRuleViolationException)

    def test_rule(self) -> None:
        exc = SprintNotStartedException()
        assert exc.rule == "SprintNotStarted"


@pytest.mark.unit
class TestCannotCompleteSprintWithOpenTasksException:
    def test_is_business_rule(self) -> None:
        exc = CannotCompleteSprintWithOpenTasksException()
        assert isinstance(exc, BusinessRuleViolationException)

    def test_rule(self) -> None:
        exc = CannotCompleteSprintWithOpenTasksException()
        assert exc.rule == "NoCompleteSprintWithOpenTasks"

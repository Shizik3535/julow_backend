"""Unit-тесты для исключений Board aggregate (Project BC)."""

import pytest

from app.shared.domain.base_exceptions import DomainException
from app.shared.domain.exceptions import BusinessRuleViolationException, EntityNotFoundException
from app.context.project.domain.exceptions.board_exceptions import (
    BoardColumnNotFoundException,
    SwimlaneNotFoundException,
    WorkflowStatusNotFoundException,
    WorkflowTransitionNotAllowedException,
    CircularTransitionException,
    WIPLimitExceededException,
)


@pytest.mark.unit
class TestBoardColumnNotFoundException:
    def test_is_entity_not_found(self) -> None:
        exc = BoardColumnNotFoundException(id="col-1")
        assert isinstance(exc, EntityNotFoundException)
        assert exc.entity_type == "BoardColumn"

    def test_message_contains_id(self) -> None:
        exc = BoardColumnNotFoundException(id="col-1")
        assert "col-1" in exc.message


@pytest.mark.unit
class TestSwimlaneNotFoundException:
    def test_is_entity_not_found(self) -> None:
        exc = SwimlaneNotFoundException(id="sw-1")
        assert isinstance(exc, EntityNotFoundException)
        assert exc.entity_type == "Swimlane"


@pytest.mark.unit
class TestWorkflowStatusNotFoundException:
    def test_is_entity_not_found(self) -> None:
        exc = WorkflowStatusNotFoundException(id="ws-1")
        assert isinstance(exc, EntityNotFoundException)
        assert exc.entity_type == "WorkflowStatus"


@pytest.mark.unit
class TestWorkflowTransitionNotAllowedException:
    def test_is_business_rule(self) -> None:
        exc = WorkflowTransitionNotAllowedException()
        assert isinstance(exc, BusinessRuleViolationException)

    def test_rule(self) -> None:
        exc = WorkflowTransitionNotAllowedException()
        assert exc.rule == "WorkflowTransitionNotAllowed"

    def test_message_with_reason(self) -> None:
        exc = WorkflowTransitionNotAllowedException(reason="no permission")
        assert "no permission" in exc.message


@pytest.mark.unit
class TestCircularTransitionException:
    def test_is_business_rule(self) -> None:
        exc = CircularTransitionException()
        assert isinstance(exc, BusinessRuleViolationException)

    def test_rule(self) -> None:
        exc = CircularTransitionException()
        assert exc.rule == "NoCircularTransition"


@pytest.mark.unit
class TestWIPLimitExceededException:
    def test_is_business_rule(self) -> None:
        exc = WIPLimitExceededException()
        assert isinstance(exc, BusinessRuleViolationException)

    def test_rule(self) -> None:
        exc = WIPLimitExceededException()
        assert exc.rule == "WIPLimit"

    def test_message_with_column_name(self) -> None:
        exc = WIPLimitExceededException(column_name="In Progress")
        assert "In Progress" in exc.message

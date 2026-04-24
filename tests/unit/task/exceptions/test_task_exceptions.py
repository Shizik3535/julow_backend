"""Unit-тесты для исключений Task aggregate (Task BC)."""

import pytest

from app.shared.domain.base_exceptions import DomainException
from app.shared.domain.exceptions import BusinessRuleViolationException, EntityNotFoundException
from app.context.task.domain.exceptions.task_exceptions import (
    TaskNotFoundException,
    TaskArchivedException,
    CannotChangeStatusException,
    CircularDependencyException,
    TaskHierarchyDepthExceededException,
    InvalidTaskRelationException,
    CannotRelateTaskToSelfException,
    DuplicateRelationException,
    ChecklistNotFoundException,
    ChecklistItemNotFoundException,
    DuplicateWatcherException,
    DuplicateLabelException,
    EffortUnitMismatchException,
    InvalidEffortValueException,
    RecurringTaskConfigurationException,
    AttachmentNotFoundException,
)


@pytest.mark.unit
class TestTaskNotFoundException:
    def test_is_entity_not_found(self) -> None:
        exc = TaskNotFoundException(id="abc-123")
        assert isinstance(exc, EntityNotFoundException)
        assert exc.entity_type == "Task"

    def test_message_contains_id(self) -> None:
        exc = TaskNotFoundException(id="abc-123")
        assert "abc-123" in exc.message


@pytest.mark.unit
class TestTaskArchivedException:
    def test_is_domain(self) -> None:
        exc = TaskArchivedException()
        assert isinstance(exc, DomainException)

    def test_message(self) -> None:
        exc = TaskArchivedException()
        assert "архивирована" in exc.message.lower()


@pytest.mark.unit
class TestCannotChangeStatusException:
    def test_is_domain(self) -> None:
        exc = CannotChangeStatusException()
        assert isinstance(exc, DomainException)

    def test_message_with_reason(self) -> None:
        exc = CannotChangeStatusException(reason="invalid transition")
        assert "invalid transition" in exc.message

    def test_message_without_reason(self) -> None:
        exc = CannotChangeStatusException()
        assert "не разрешён" in exc.message.lower()


@pytest.mark.unit
class TestCircularDependencyException:
    def test_is_business_rule(self) -> None:
        exc = CircularDependencyException()
        assert isinstance(exc, BusinessRuleViolationException)
        assert exc.rule == "NoCircularDependency"


@pytest.mark.unit
class TestTaskHierarchyDepthExceededException:
    def test_is_business_rule(self) -> None:
        exc = TaskHierarchyDepthExceededException()
        assert isinstance(exc, BusinessRuleViolationException)
        assert exc.rule == "MaxTaskHierarchyDepth"

    def test_message_with_max_depth(self) -> None:
        exc = TaskHierarchyDepthExceededException(max_depth=5)
        assert "5" in exc.message

    def test_message_without_max_depth(self) -> None:
        exc = TaskHierarchyDepthExceededException()
        assert "глубина" in exc.message.lower()


@pytest.mark.unit
class TestInvalidTaskRelationException:
    def test_is_business_rule(self) -> None:
        exc = InvalidTaskRelationException()
        assert isinstance(exc, BusinessRuleViolationException)
        assert exc.rule == "InvalidTaskRelation"

    def test_message_with_reason(self) -> None:
        exc = InvalidTaskRelationException(reason="wrong type")
        assert "wrong type" in exc.message


@pytest.mark.unit
class TestCannotRelateTaskToSelfException:
    def test_is_business_rule(self) -> None:
        exc = CannotRelateTaskToSelfException()
        assert isinstance(exc, BusinessRuleViolationException)
        assert exc.rule == "NoSelfRelation"


@pytest.mark.unit
class TestDuplicateRelationException:
    def test_is_business_rule(self) -> None:
        exc = DuplicateRelationException()
        assert isinstance(exc, BusinessRuleViolationException)
        assert exc.rule == "UniqueRelation"


@pytest.mark.unit
class TestChecklistNotFoundException:
    def test_is_entity_not_found(self) -> None:
        exc = ChecklistNotFoundException(id="cl-1")
        assert isinstance(exc, EntityNotFoundException)
        assert exc.entity_type == "Checklist"

    def test_message_contains_id(self) -> None:
        exc = ChecklistNotFoundException(id="cl-1")
        assert "cl-1" in exc.message


@pytest.mark.unit
class TestChecklistItemNotFoundException:
    def test_is_entity_not_found(self) -> None:
        exc = ChecklistItemNotFoundException(id="item-1")
        assert isinstance(exc, EntityNotFoundException)
        assert exc.entity_type == "ChecklistItem"

    def test_message_contains_id(self) -> None:
        exc = ChecklistItemNotFoundException(id="item-1")
        assert "item-1" in exc.message


@pytest.mark.unit
class TestDuplicateWatcherException:
    def test_is_business_rule(self) -> None:
        exc = DuplicateWatcherException()
        assert isinstance(exc, BusinessRuleViolationException)
        assert exc.rule == "UniqueWatcher"

    def test_message_contains_user_id(self) -> None:
        exc = DuplicateWatcherException(user_id="user-1")
        assert "user-1" in exc.message


@pytest.mark.unit
class TestDuplicateLabelException:
    def test_is_business_rule(self) -> None:
        exc = DuplicateLabelException()
        assert isinstance(exc, BusinessRuleViolationException)
        assert exc.rule == "UniqueLabel"

    def test_message_contains_name(self) -> None:
        exc = DuplicateLabelException(name="bug")
        assert "bug" in exc.message


@pytest.mark.unit
class TestEffortUnitMismatchException:
    def test_is_business_rule(self) -> None:
        exc = EffortUnitMismatchException()
        assert isinstance(exc, BusinessRuleViolationException)
        assert exc.rule == "EffortUnitMatch"


@pytest.mark.unit
class TestInvalidEffortValueException:
    def test_is_business_rule(self) -> None:
        exc = InvalidEffortValueException()
        assert isinstance(exc, BusinessRuleViolationException)
        assert exc.rule == "ValidEffortValue"

    def test_message_with_detail(self) -> None:
        exc = InvalidEffortValueException(detail="negative")
        assert "negative" in exc.message


@pytest.mark.unit
class TestRecurringTaskConfigurationException:
    def test_is_business_rule(self) -> None:
        exc = RecurringTaskConfigurationException()
        assert isinstance(exc, BusinessRuleViolationException)
        assert exc.rule == "ValidRecurrenceConfig"

    def test_message_with_detail(self) -> None:
        exc = RecurringTaskConfigurationException(detail="bad interval")
        assert "bad interval" in exc.message


@pytest.mark.unit
class TestAttachmentNotFoundException:
    def test_is_entity_not_found(self) -> None:
        exc = AttachmentNotFoundException(id="att-1")
        assert isinstance(exc, EntityNotFoundException)
        assert exc.entity_type == "TaskAttachment"

    def test_message_contains_id(self) -> None:
        exc = AttachmentNotFoundException(id="att-1")
        assert "att-1" in exc.message

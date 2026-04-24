"""Unit-тесты для исключений ProjectMembership aggregate (Project BC)."""

import pytest

from app.shared.domain.exceptions import BusinessRuleViolationException, EntityNotFoundException
from app.context.project.domain.exceptions.project_membership_exceptions import (
    ProjectMemberNotFoundException,
    CannotRemoveOwnerAsMemberException,
    CannotRemoveLastOwnerException,
)


@pytest.mark.unit
class TestProjectMemberNotFoundException:
    def test_is_entity_not_found(self) -> None:
        exc = ProjectMemberNotFoundException(id="user-1")
        assert isinstance(exc, EntityNotFoundException)
        assert exc.entity_type == "ProjectMember"

    def test_message_contains_id(self) -> None:
        exc = ProjectMemberNotFoundException(id="user-1")
        assert "user-1" in exc.message


@pytest.mark.unit
class TestCannotRemoveOwnerAsMemberException:
    def test_is_business_rule(self) -> None:
        exc = CannotRemoveOwnerAsMemberException()
        assert isinstance(exc, BusinessRuleViolationException)

    def test_rule(self) -> None:
        exc = CannotRemoveOwnerAsMemberException()
        assert exc.rule == "OwnerCannotBeRemovedAsMember"

    def test_message_with_user_id(self) -> None:
        exc = CannotRemoveOwnerAsMemberException(user_id="user-1")
        assert "user-1" in exc.message


@pytest.mark.unit
class TestCannotRemoveLastOwnerException:
    def test_is_business_rule(self) -> None:
        exc = CannotRemoveLastOwnerException()
        assert isinstance(exc, BusinessRuleViolationException)

    def test_rule(self) -> None:
        exc = CannotRemoveLastOwnerException()
        assert exc.rule == "AtLeastOneOwner"

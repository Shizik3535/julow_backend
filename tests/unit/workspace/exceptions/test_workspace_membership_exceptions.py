"""Unit-тесты для исключений WorkspaceMembership aggregate (Workspace BC)."""

import pytest

from app.shared.domain.exceptions import BusinessRuleViolationException, EntityNotFoundException
from app.context.workspace.domain.exceptions.workspace_membership_exceptions import (
    WorkspaceMemberNotFoundException,
    CannotRemoveOwnerAsMemberException,
    MembershipLimitExceededException,
    EmailDomainNotAllowedException,
)


@pytest.mark.unit
class TestWorkspaceMemberNotFoundException:
    def test_is_entity_not_found(self) -> None:
        exc = WorkspaceMemberNotFoundException(id="m1")
        assert isinstance(exc, EntityNotFoundException)
        assert exc.entity_type == "WorkspaceMember"

    def test_message_contains_id(self) -> None:
        exc = WorkspaceMemberNotFoundException(id="m1")
        assert "m1" in exc.message


@pytest.mark.unit
class TestCannotRemoveOwnerAsMemberException:
    def test_is_business_rule(self) -> None:
        exc = CannotRemoveOwnerAsMemberException(user_id="u1")
        assert isinstance(exc, BusinessRuleViolationException)
        assert exc.rule == "OwnerCannotBeRemovedAsMember"

    def test_message_contains_user_id(self) -> None:
        exc = CannotRemoveOwnerAsMemberException(user_id="u1")
        assert "u1" in exc.message


@pytest.mark.unit
class TestMembershipLimitExceededException:
    def test_is_business_rule(self) -> None:
        exc = MembershipLimitExceededException(max_members=50)
        assert isinstance(exc, BusinessRuleViolationException)
        assert exc.rule == "MaxMembers"

    def test_message_contains_max_members(self) -> None:
        exc = MembershipLimitExceededException(max_members=50)
        assert "50" in exc.message


@pytest.mark.unit
class TestEmailDomainNotAllowedException:
    def test_is_business_rule(self) -> None:
        exc = EmailDomainNotAllowedException(domain="spam.com")
        assert isinstance(exc, BusinessRuleViolationException)
        assert exc.rule == "AllowedEmailDomains"

    def test_message_contains_domain(self) -> None:
        exc = EmailDomainNotAllowedException(domain="spam.com")
        assert "spam.com" in exc.message

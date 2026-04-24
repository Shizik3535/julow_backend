"""Unit-тесты для исключений Invitation aggregate (Organization BC)."""

import pytest

from app.shared.domain.base_exceptions import DomainException
from app.shared.domain.exceptions import BusinessRuleViolationException, EntityNotFoundException
from app.context.organization.domain.exceptions.invitation_exceptions import (
    InvitationNotFoundException,
    InvitationExpiredException,
    InvitationLinkExpiredException,
    InvitationLinkMaxUsesExceededException,
    DuplicateInvitationException,
    CircularDepartmentException,
)


@pytest.mark.unit
class TestInvitationNotFoundException:
    def test_is_entity_not_found(self) -> None:
        exc = InvitationNotFoundException(id="inv-1")
        assert isinstance(exc, EntityNotFoundException)
        assert exc.entity_type == "Invitation"

    def test_message_contains_id(self) -> None:
        exc = InvitationNotFoundException(id="inv-1")
        assert "inv-1" in exc.message


@pytest.mark.unit
class TestInvitationExpiredException:
    def test_is_domain_exception(self) -> None:
        exc = InvitationExpiredException()
        assert isinstance(exc, DomainException)

    def test_message(self) -> None:
        exc = InvitationExpiredException()
        assert "истекло" in exc.message.lower()


@pytest.mark.unit
class TestInvitationLinkExpiredException:
    def test_is_domain_exception(self) -> None:
        exc = InvitationLinkExpiredException()
        assert isinstance(exc, DomainException)

    def test_message(self) -> None:
        exc = InvitationLinkExpiredException()
        assert "истекла" in exc.message.lower()


@pytest.mark.unit
class TestInvitationLinkMaxUsesExceededException:
    def test_is_business_rule(self) -> None:
        exc = InvitationLinkMaxUsesExceededException()
        assert isinstance(exc, BusinessRuleViolationException)

    def test_rule(self) -> None:
        exc = InvitationLinkMaxUsesExceededException()
        assert exc.rule == "InvitationLinkMaxUses"


@pytest.mark.unit
class TestDuplicateInvitationException:
    def test_is_business_rule(self) -> None:
        exc = DuplicateInvitationException(email="test@example.com")
        assert isinstance(exc, BusinessRuleViolationException)

    def test_rule(self) -> None:
        exc = DuplicateInvitationException()
        assert exc.rule == "UniqueInvitation"

    def test_message_contains_email(self) -> None:
        exc = DuplicateInvitationException(email="test@example.com")
        assert "test@example.com" in exc.message


@pytest.mark.unit
class TestCircularDepartmentException:
    def test_is_business_rule(self) -> None:
        exc = CircularDepartmentException()
        assert isinstance(exc, BusinessRuleViolationException)

    def test_rule(self) -> None:
        exc = CircularDepartmentException()
        assert exc.rule == "NoCircularDepartmentReference"

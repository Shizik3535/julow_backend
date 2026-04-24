"""Unit-тесты для исключений WorkspaceInvitation aggregate (Workspace BC)."""

import pytest

from app.shared.domain.base_exceptions import DomainException
from app.shared.domain.exceptions import BusinessRuleViolationException, EntityNotFoundException
from app.context.workspace.domain.exceptions.workspace_invitation_exceptions import (
    InvitationNotFoundException,
    InvitationExpiredException,
    InvitationLinkExpiredException,
    InvitationLinkMaxUsesExceededException,
    DuplicateInvitationException,
)


@pytest.mark.unit
class TestInvitationNotFoundException:
    def test_is_entity_not_found(self) -> None:
        exc = InvitationNotFoundException(id="inv-1")
        assert isinstance(exc, EntityNotFoundException)
        assert exc.entity_type == "WorkspaceInvitation"

    def test_message_contains_id(self) -> None:
        exc = InvitationNotFoundException(id="inv-1")
        assert "inv-1" in exc.message


@pytest.mark.unit
class TestInvitationExpiredException:
    def test_is_domain(self) -> None:
        exc = InvitationExpiredException()
        assert isinstance(exc, DomainException)
        assert "истекло" in exc.message.lower()


@pytest.mark.unit
class TestInvitationLinkExpiredException:
    def test_is_domain(self) -> None:
        exc = InvitationLinkExpiredException()
        assert isinstance(exc, DomainException)
        assert "истекла" in exc.message.lower()


@pytest.mark.unit
class TestInvitationLinkMaxUsesExceededException:
    def test_is_business_rule(self) -> None:
        exc = InvitationLinkMaxUsesExceededException()
        assert isinstance(exc, BusinessRuleViolationException)
        assert exc.rule == "InvitationLinkMaxUses"


@pytest.mark.unit
class TestDuplicateInvitationException:
    def test_is_business_rule(self) -> None:
        exc = DuplicateInvitationException(email="a@b.com")
        assert isinstance(exc, BusinessRuleViolationException)
        assert exc.rule == "UniqueInvitation"

    def test_message_contains_email(self) -> None:
        exc = DuplicateInvitationException(email="a@b.com")
        assert "a@b.com" in exc.message

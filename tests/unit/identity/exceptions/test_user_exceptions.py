"""Unit-тесты для исключений User aggregate (Identity BC)."""

import pytest

from app.shared.domain.base_exceptions import DomainException
from app.shared.domain.exceptions import BusinessRuleViolationException
from app.shared.domain.exceptions import EntityNotFoundException
from app.context.identity.domain.exceptions.user_exceptions import (
    AccountDeletionPendingException,
    CannotUnlinkLastProviderException,
    DuplicateRoleException,
    EmailNotConfirmedException,
    InvalidBackupCodeException,
    InvalidCredentialsException,
    InvalidVerificationTokenException,
    LastSystemRoleException,
    RoleNotFoundException,
    UserBlockedException,
    UserNotFoundException,
)


@pytest.mark.unit
class TestUserNotFoundException:
    def test_is_entity_not_found(self) -> None:
        exc = UserNotFoundException(id="abc-123")
        assert isinstance(exc, EntityNotFoundException)
        assert exc.entity_type == "User"


@pytest.mark.unit
class TestInvalidCredentialsException:
    def test_is_domain(self) -> None:
        exc = InvalidCredentialsException()
        assert isinstance(exc, DomainException)


@pytest.mark.unit
class TestUserBlockedException:
    def test_with_until(self) -> None:
        exc = UserBlockedException(locked_until="2025-12-31")
        assert isinstance(exc, DomainException)
        assert "2025-12-31" in exc.message

    def test_without_until(self) -> None:
        exc = UserBlockedException()
        assert "заблокир" in exc.message.lower()


@pytest.mark.unit
class TestEmailNotConfirmedException:
    def test_is_domain(self) -> None:
        exc = EmailNotConfirmedException()
        assert isinstance(exc, DomainException)


@pytest.mark.unit
class TestInvalidVerificationTokenException:
    def test_is_domain(self) -> None:
        exc = InvalidVerificationTokenException()
        assert isinstance(exc, DomainException)


@pytest.mark.unit
class TestAccountDeletionPendingException:
    def test_is_domain(self) -> None:
        exc = AccountDeletionPendingException()
        assert isinstance(exc, DomainException)


@pytest.mark.unit
class TestRoleNotFoundException:
    def test_is_entity_not_found(self) -> None:
        exc = RoleNotFoundException(id="role-123")
        assert isinstance(exc, EntityNotFoundException)
        assert exc.entity_type == "Role"


@pytest.mark.unit
class TestDuplicateRoleException:
    def test_is_business_rule(self) -> None:
        exc = DuplicateRoleException()
        assert isinstance(exc, BusinessRuleViolationException)


@pytest.mark.unit
class TestLastSystemRoleException:
    def test_is_business_rule(self) -> None:
        exc = LastSystemRoleException()
        assert isinstance(exc, BusinessRuleViolationException)


@pytest.mark.unit
class TestCannotUnlinkLastProviderException:
    def test_is_business_rule(self) -> None:
        exc = CannotUnlinkLastProviderException()
        assert isinstance(exc, BusinessRuleViolationException)


@pytest.mark.unit
class TestInvalidBackupCodeException:
    def test_is_domain(self) -> None:
        exc = InvalidBackupCodeException()
        assert isinstance(exc, DomainException)

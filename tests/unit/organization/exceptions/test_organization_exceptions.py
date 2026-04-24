"""Unit-тесты для исключений Organization aggregate (Organization BC)."""

import pytest

from app.shared.domain.base_exceptions import DomainException
from app.shared.domain.exceptions import BusinessRuleViolationException, EntityNotFoundException
from app.context.organization.domain.exceptions.organization_exceptions import (
    OrganizationNotFoundException,
    OrganizationSuspendedException,
    CannotRemoveOwnerException,
    CannotRemoveLastOwnerException,
    CannotTransferOwnershipException,
    SecurityPolicyViolationException,
    SSOProviderAlreadyExistsException,
    StorageQuotaExceededException,
)


@pytest.mark.unit
class TestOrganizationNotFoundException:
    def test_is_entity_not_found(self) -> None:
        exc = OrganizationNotFoundException(id="abc-123")
        assert isinstance(exc, EntityNotFoundException)
        assert exc.entity_type == "Organization"

    def test_message_contains_id(self) -> None:
        exc = OrganizationNotFoundException(id="abc-123")
        assert "abc-123" in exc.message


@pytest.mark.unit
class TestOrganizationSuspendedException:
    def test_is_domain_exception(self) -> None:
        exc = OrganizationSuspendedException()
        assert isinstance(exc, DomainException)

    def test_message(self) -> None:
        exc = OrganizationSuspendedException()
        assert "приостановлена" in exc.message.lower()


@pytest.mark.unit
class TestCannotRemoveOwnerException:
    def test_is_business_rule(self) -> None:
        exc = CannotRemoveOwnerException(user_id="user-1")
        assert isinstance(exc, BusinessRuleViolationException)

    def test_rule(self) -> None:
        exc = CannotRemoveOwnerException()
        assert exc.rule == "OwnerCannotBeRemoved"

    def test_message_contains_user_id(self) -> None:
        exc = CannotRemoveOwnerException(user_id="user-1")
        assert "user-1" in exc.message


@pytest.mark.unit
class TestCannotRemoveLastOwnerException:
    def test_is_business_rule(self) -> None:
        exc = CannotRemoveLastOwnerException()
        assert isinstance(exc, BusinessRuleViolationException)

    def test_rule(self) -> None:
        exc = CannotRemoveLastOwnerException()
        assert exc.rule == "AtLeastOneOwner"


@pytest.mark.unit
class TestCannotTransferOwnershipException:
    def test_is_business_rule(self) -> None:
        exc = CannotTransferOwnershipException(reason="test")
        assert isinstance(exc, BusinessRuleViolationException)

    def test_rule(self) -> None:
        exc = CannotTransferOwnershipException()
        assert exc.rule == "OwnershipTransfer"

    def test_message_contains_reason(self) -> None:
        exc = CannotTransferOwnershipException(reason="not owner")
        assert "not owner" in exc.message


@pytest.mark.unit
class TestSecurityPolicyViolationException:
    def test_is_domain_exception(self) -> None:
        exc = SecurityPolicyViolationException()
        assert isinstance(exc, DomainException)

    def test_message_with_detail(self) -> None:
        exc = SecurityPolicyViolationException(detail="weak password")
        assert "weak password" in exc.message


@pytest.mark.unit
class TestSSOProviderAlreadyExistsException:
    def test_is_business_rule(self) -> None:
        exc = SSOProviderAlreadyExistsException(provider="SAML")
        assert isinstance(exc, BusinessRuleViolationException)

    def test_rule(self) -> None:
        exc = SSOProviderAlreadyExistsException()
        assert exc.rule == "UniqueSSOProvider"

    def test_message_contains_provider(self) -> None:
        exc = SSOProviderAlreadyExistsException(provider="SAML")
        assert "SAML" in exc.message


@pytest.mark.unit
class TestStorageQuotaExceededException:
    def test_is_business_rule(self) -> None:
        exc = StorageQuotaExceededException()
        assert isinstance(exc, BusinessRuleViolationException)

    def test_rule(self) -> None:
        exc = StorageQuotaExceededException()
        assert exc.rule == "StorageQuota"

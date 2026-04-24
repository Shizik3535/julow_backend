"""Unit-тесты для исключений Workspace aggregate (Workspace BC)."""

import pytest

from app.shared.domain.base_exceptions import DomainException
from app.shared.domain.exceptions import BusinessRuleViolationException, EntityNotFoundException
from app.context.workspace.domain.exceptions.workspace_exceptions import (
    WorkspaceNotFoundException,
    WorkspaceSuspendedException,
    WorkspaceArchivedException,
    CannotRemoveOwnerException,
    CannotRemoveLastOwnerException,
    CannotTransferOwnershipException,
    SecurityPolicyViolationException,
    IPAllowlistViolationException,
    SSORequiredException,
    CircularWorkspaceHierarchyException,
    ParentWorkspaceNotFoundException,
    CannotArchiveWithChildrenException,
    WorkspaceLimitExceededException,
)


@pytest.mark.unit
class TestWorkspaceNotFoundException:
    def test_is_entity_not_found(self) -> None:
        exc = WorkspaceNotFoundException(id="abc-123")
        assert isinstance(exc, EntityNotFoundException)
        assert exc.entity_type == "Workspace"

    def test_message_contains_id(self) -> None:
        exc = WorkspaceNotFoundException(id="abc-123")
        assert "abc-123" in exc.message


@pytest.mark.unit
class TestWorkspaceSuspendedException:
    def test_is_domain(self) -> None:
        exc = WorkspaceSuspendedException()
        assert isinstance(exc, DomainException)
        assert "приостановлен" in exc.message.lower()


@pytest.mark.unit
class TestWorkspaceArchivedException:
    def test_is_domain(self) -> None:
        exc = WorkspaceArchivedException()
        assert isinstance(exc, DomainException)
        assert "архивирован" in exc.message.lower()


@pytest.mark.unit
class TestCannotRemoveOwnerException:
    def test_is_business_rule(self) -> None:
        exc = CannotRemoveOwnerException(user_id="u1")
        assert isinstance(exc, BusinessRuleViolationException)
        assert exc.rule == "OwnerCannotBeRemoved"

    def test_message_contains_user_id(self) -> None:
        exc = CannotRemoveOwnerException(user_id="u1")
        assert "u1" in exc.message


@pytest.mark.unit
class TestCannotRemoveLastOwnerException:
    def test_is_business_rule(self) -> None:
        exc = CannotRemoveLastOwnerException()
        assert isinstance(exc, BusinessRuleViolationException)
        assert exc.rule == "AtLeastOneOwner"


@pytest.mark.unit
class TestCannotTransferOwnershipException:
    def test_is_business_rule(self) -> None:
        exc = CannotTransferOwnershipException(reason="test")
        assert isinstance(exc, BusinessRuleViolationException)
        assert exc.rule == "OwnershipTransfer"

    def test_message_contains_reason(self) -> None:
        exc = CannotTransferOwnershipException(reason="not owner")
        assert "not owner" in exc.message


@pytest.mark.unit
class TestSecurityPolicyViolationException:
    def test_is_domain(self) -> None:
        exc = SecurityPolicyViolationException(detail="2fa")
        assert isinstance(exc, DomainException)
        assert "2fa" in exc.message


@pytest.mark.unit
class TestIPAllowlistViolationException:
    def test_is_domain(self) -> None:
        exc = IPAllowlistViolationException(ip="1.2.3.4")
        assert isinstance(exc, DomainException)
        assert "1.2.3.4" in exc.message


@pytest.mark.unit
class TestSSORequiredException:
    def test_is_domain(self) -> None:
        exc = SSORequiredException()
        assert isinstance(exc, DomainException)
        assert "sso" in exc.message.lower()


@pytest.mark.unit
class TestCircularWorkspaceHierarchyException:
    def test_is_business_rule(self) -> None:
        exc = CircularWorkspaceHierarchyException()
        assert isinstance(exc, BusinessRuleViolationException)
        assert exc.rule == "NoCircularWorkspaceReference"


@pytest.mark.unit
class TestParentWorkspaceNotFoundException:
    def test_is_entity_not_found(self) -> None:
        exc = ParentWorkspaceNotFoundException(id="p1")
        assert isinstance(exc, EntityNotFoundException)
        assert exc.entity_type == "Workspace"

    def test_message_contains_id(self) -> None:
        exc = ParentWorkspaceNotFoundException(id="p1")
        assert "p1" in exc.message


@pytest.mark.unit
class TestCannotArchiveWithChildrenException:
    def test_is_business_rule(self) -> None:
        exc = CannotArchiveWithChildrenException()
        assert isinstance(exc, BusinessRuleViolationException)
        assert exc.rule == "NoArchiveWithChildren"


@pytest.mark.unit
class TestWorkspaceLimitExceededException:
    def test_is_business_rule(self) -> None:
        exc = WorkspaceLimitExceededException(limit_name="max_members")
        assert isinstance(exc, BusinessRuleViolationException)
        assert exc.rule == "WorkspaceLimit"

    def test_message_contains_limit_name(self) -> None:
        exc = WorkspaceLimitExceededException(limit_name="max_members")
        assert "max_members" in exc.message

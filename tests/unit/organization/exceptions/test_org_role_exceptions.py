"""Unit-тесты для исключений OrgRole aggregate (Organization BC)."""

import pytest

from app.shared.domain.exceptions import BusinessRuleViolationException, EntityNotFoundException
from app.context.organization.domain.exceptions.org_role_exceptions import (
    OrgRoleNotFoundException,
    OrgRoleInUseException,
    CannotDeleteSystemRoleException,
)


@pytest.mark.unit
class TestOrgRoleNotFoundException:
    def test_is_entity_not_found(self) -> None:
        exc = OrgRoleNotFoundException(id="role-1")
        assert isinstance(exc, EntityNotFoundException)
        assert exc.entity_type == "OrgRole"

    def test_message_contains_id(self) -> None:
        exc = OrgRoleNotFoundException(id="role-1")
        assert "role-1" in exc.message


@pytest.mark.unit
class TestOrgRoleInUseException:
    def test_is_business_rule(self) -> None:
        exc = OrgRoleInUseException(role_name="admin")
        assert isinstance(exc, BusinessRuleViolationException)

    def test_rule(self) -> None:
        exc = OrgRoleInUseException()
        assert exc.rule == "RoleInUse"

    def test_message_contains_role_name(self) -> None:
        exc = OrgRoleInUseException(role_name="admin")
        assert "admin" in exc.message


@pytest.mark.unit
class TestCannotDeleteSystemRoleException:
    def test_is_business_rule(self) -> None:
        exc = CannotDeleteSystemRoleException(role_name="owner")
        assert isinstance(exc, BusinessRuleViolationException)

    def test_rule(self) -> None:
        exc = CannotDeleteSystemRoleException()
        assert exc.rule == "SystemRoleCannotBeDeleted"

    def test_message_contains_role_name(self) -> None:
        exc = CannotDeleteSystemRoleException(role_name="owner")
        assert "owner" in exc.message

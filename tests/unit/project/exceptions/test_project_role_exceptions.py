"""Unit-тесты для исключений ProjectRole aggregate (Project BC)."""

import pytest

from app.shared.domain.exceptions import BusinessRuleViolationException, EntityNotFoundException
from app.context.project.domain.exceptions.project_role_exceptions import (
    ProjectRoleNotFoundException,
    ProjectRoleInUseException,
    CannotDeleteSystemRoleException,
)


@pytest.mark.unit
class TestProjectRoleNotFoundException:
    def test_is_entity_not_found(self) -> None:
        exc = ProjectRoleNotFoundException(id="role-1")
        assert isinstance(exc, EntityNotFoundException)
        assert exc.entity_type == "ProjectRole"

    def test_message_contains_id(self) -> None:
        exc = ProjectRoleNotFoundException(id="role-1")
        assert "role-1" in exc.message


@pytest.mark.unit
class TestProjectRoleInUseException:
    def test_is_business_rule(self) -> None:
        exc = ProjectRoleInUseException()
        assert isinstance(exc, BusinessRuleViolationException)

    def test_rule(self) -> None:
        exc = ProjectRoleInUseException()
        assert exc.rule == "RoleInUse"

    def test_message_with_role_name(self) -> None:
        exc = ProjectRoleInUseException(role_name="admin")
        assert "admin" in exc.message


@pytest.mark.unit
class TestCannotDeleteSystemRoleException:
    def test_is_business_rule(self) -> None:
        exc = CannotDeleteSystemRoleException()
        assert isinstance(exc, BusinessRuleViolationException)

    def test_rule(self) -> None:
        exc = CannotDeleteSystemRoleException()
        assert exc.rule == "SystemRoleCannotBeDeleted"

    def test_message_with_role_name(self) -> None:
        exc = CannotDeleteSystemRoleException(role_name="owner")
        assert "owner" in exc.message

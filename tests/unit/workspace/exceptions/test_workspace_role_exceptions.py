"""Unit-тесты для исключений WorkspaceRole aggregate (Workspace BC)."""

import pytest

from app.shared.domain.exceptions import BusinessRuleViolationException, EntityNotFoundException
from app.context.workspace.domain.exceptions.workspace_role_exceptions import (
    WorkspaceRoleNotFoundException,
    WorkspaceRoleInUseException,
    CannotDeleteSystemRoleException,
)


@pytest.mark.unit
class TestWorkspaceRoleNotFoundException:
    def test_is_entity_not_found(self) -> None:
        exc = WorkspaceRoleNotFoundException(id="r1")
        assert isinstance(exc, EntityNotFoundException)
        assert exc.entity_type == "WorkspaceRole"

    def test_message_contains_id(self) -> None:
        exc = WorkspaceRoleNotFoundException(id="r1")
        assert "r1" in exc.message


@pytest.mark.unit
class TestWorkspaceRoleInUseException:
    def test_is_business_rule(self) -> None:
        exc = WorkspaceRoleInUseException(role_name="admin")
        assert isinstance(exc, BusinessRuleViolationException)
        assert exc.rule == "RoleInUse"

    def test_message_contains_role_name(self) -> None:
        exc = WorkspaceRoleInUseException(role_name="admin")
        assert "admin" in exc.message


@pytest.mark.unit
class TestCannotDeleteSystemRoleException:
    def test_is_business_rule(self) -> None:
        exc = CannotDeleteSystemRoleException(role_name="owner")
        assert isinstance(exc, BusinessRuleViolationException)
        assert exc.rule == "SystemRoleCannotBeDeleted"

    def test_message_contains_role_name(self) -> None:
        exc = CannotDeleteSystemRoleException(role_name="owner")
        assert "owner" in exc.message

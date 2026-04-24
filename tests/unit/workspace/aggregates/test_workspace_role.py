"""Unit-тесты для агрегата WorkspaceRole (Workspace BC)."""

import pytest

from app.context.workspace.domain.aggregates.workspace_role import WorkspaceRole
from app.context.workspace.domain.events.workspace_role_events import (
    WorkspaceRoleCreated,
    WorkspaceRoleUpdated,
    WorkspaceRoleDeleted,
)
from app.context.workspace.domain.exceptions.workspace_role_exceptions import (
    CannotDeleteSystemRoleException,
)


# ═══════════════════════════════════════════════════════════════════════════
# Системная роль
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestSystemRoleCreation:
    def test_create_system_role(self, system_role: WorkspaceRole) -> None:
        assert system_role.name == "owner"
        assert system_role.is_system is True
        assert system_role.workspace_id is None

    def test_create_system_role_emits_created(self, system_role: WorkspaceRole) -> None:
        events = system_role.clear_domain_events()
        assert any(isinstance(e, WorkspaceRoleCreated) for e in events)

    def test_system_role_is_system(self, system_role: WorkspaceRole) -> None:
        assert system_role.is_system is True


# ═══════════════════════════════════════════════════════════════════════════
# Кастомная роль
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestCustomRoleCreation:
    def test_create_custom_role(self, custom_role: WorkspaceRole) -> None:
        assert custom_role.name == "custom_role"
        assert custom_role.is_system is False
        assert custom_role.workspace_id is not None

    def test_create_custom_role_emits_created(self, custom_role: WorkspaceRole) -> None:
        events = custom_role.clear_domain_events()
        assert any(isinstance(e, WorkspaceRoleCreated) for e in events)

    def test_custom_role_is_not_system(self, custom_role: WorkspaceRole) -> None:
        assert custom_role.is_system is False


# ═══════════════════════════════════════════════════════════════════════════
# Обновление роли
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestRoleUpdate:
    def test_update_permissions(self, custom_role: WorkspaceRole) -> None:
        custom_role.clear_domain_events()
        custom_role.update(permissions=["read", "write"])
        assert custom_role.permissions == ["read", "write"]

    def test_update_description(self, custom_role: WorkspaceRole) -> None:
        custom_role.clear_domain_events()
        custom_role.update(description="New desc")
        assert custom_role.description == "New desc"

    def test_update_emits_event(self, custom_role: WorkspaceRole) -> None:
        custom_role.clear_domain_events()
        custom_role.update(permissions=["read", "write"])
        events = custom_role.clear_domain_events()
        assert any(isinstance(e, WorkspaceRoleUpdated) for e in events)


# ═══════════════════════════════════════════════════════════════════════════
# Удаление роли
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestRoleDeletion:
    def test_can_be_deleted_custom(self, custom_role: WorkspaceRole) -> None:
        assert custom_role.can_be_deleted() is True

    def test_cannot_be_deleted_system(self, system_role: WorkspaceRole) -> None:
        assert system_role.can_be_deleted() is False

    def test_assert_deletable_custom_passes(self, custom_role: WorkspaceRole) -> None:
        custom_role.assert_deletable()

    def test_assert_deletable_system_raises(self, system_role: WorkspaceRole) -> None:
        with pytest.raises(CannotDeleteSystemRoleException):
            system_role.assert_deletable()

    def test_mark_deleted_custom(self, custom_role: WorkspaceRole) -> None:
        custom_role.clear_domain_events()
        custom_role.mark_deleted()
        events = custom_role.clear_domain_events()
        assert any(isinstance(e, WorkspaceRoleDeleted) for e in events)

    def test_mark_deleted_system_raises(self, system_role: WorkspaceRole) -> None:
        with pytest.raises(CannotDeleteSystemRoleException):
            system_role.mark_deleted()

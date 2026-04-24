"""Unit-тесты для агрегата OrgRole (Organization BC)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.domain.aggregates.org_role import OrgRole
from app.context.organization.domain.value_objects.org_role_scope import OrgRoleScope
from app.context.organization.domain.events.org_role_events import (
    OrgRoleCreated,
    OrgRoleUpdated,
    OrgRoleDeleted,
)
from app.context.organization.domain.exceptions.org_role_exceptions import (
    CannotDeleteSystemRoleException,
)
from tests.factories import IdFactory


# ═══════════════════════════════════════════════════════════════════════════
# Системная роль
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestOrgRoleSystemCreation:
    def test_create_system_role(self) -> None:
        role = OrgRole.create_system(
            name="owner", permissions=["*"], scope=OrgRoleScope.ORG,
        )
        assert role.name == "owner"
        assert role.is_system is True
        assert role.org_id is None

    def test_create_system_role_emits_event(self) -> None:
        role = OrgRole.create_system(
            name="owner", permissions=["*"], scope=OrgRoleScope.ORG,
        )
        events = role.clear_domain_events()
        assert any(isinstance(e, OrgRoleCreated) for e in events)

    def test_system_role_is_system(self, system_role: OrgRole) -> None:
        assert system_role.is_system is True


# ═══════════════════════════════════════════════════════════════════════════
# Кастомная роль
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestOrgRoleCustomCreation:
    def test_create_custom_role(self, any_org_id: Id) -> None:
        role = OrgRole.create_custom(
            org_id=any_org_id, name="editor", permissions=["read", "write"],
            scope=OrgRoleScope.ORG,
        )
        assert role.name == "editor"
        assert role.is_system is False
        assert role.org_id == any_org_id

    def test_create_custom_role_emits_event(self, any_org_id: Id) -> None:
        role = OrgRole.create_custom(
            org_id=any_org_id, name="editor", permissions=["read", "write"],
            scope=OrgRoleScope.ORG,
        )
        events = role.clear_domain_events()
        assert any(isinstance(e, OrgRoleCreated) for e in events)

    def test_custom_role_is_not_system(self, custom_role: OrgRole) -> None:
        assert custom_role.is_system is False


# ═══════════════════════════════════════════════════════════════════════════
# Обновление
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestOrgRoleUpdate:
    def test_update_permissions(self, custom_role: OrgRole) -> None:
        custom_role.update(permissions=["read", "write", "delete"])
        assert custom_role.permissions == ["read", "write", "delete"]

    def test_update_description(self, custom_role: OrgRole) -> None:
        custom_role.update(description="Updated description")
        assert custom_role.description == "Updated description"

    def test_update_emits_event(self, custom_role: OrgRole) -> None:
        custom_role.update(permissions=["read"])
        events = custom_role.clear_domain_events()
        assert any(isinstance(e, OrgRoleUpdated) for e in events)


# ═══════════════════════════════════════════════════════════════════════════
# Удаление
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestOrgRoleDeletion:
    def test_can_be_deleted_custom_role(self, custom_role: OrgRole) -> None:
        assert custom_role.can_be_deleted() is True

    def test_cannot_delete_system_role(self, system_role: OrgRole) -> None:
        assert system_role.can_be_deleted() is False

    def test_mark_deleted_emits_event(self, custom_role: OrgRole) -> None:
        custom_role.mark_deleted()
        events = custom_role.clear_domain_events()
        assert any(isinstance(e, OrgRoleDeleted) for e in events)

    def test_mark_deleted_system_role_raises(self, system_role: OrgRole) -> None:
        with pytest.raises(CannotDeleteSystemRoleException):
            system_role.mark_deleted()

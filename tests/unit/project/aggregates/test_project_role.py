"""Unit-тесты для агрегата ProjectRole (Project BC)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.domain.aggregates.project_role import ProjectRole
from app.context.project.domain.events.project_role_events import (
    ProjectRoleCreated,
    ProjectRoleUpdated,
    ProjectRoleDeleted,
)
from app.context.project.domain.exceptions.project_role_exceptions import (
    CannotDeleteSystemRoleException,
)


# ═══════════════════════════════════════════════════════════════════════════
# Создание
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestProjectRoleCreation:
    def test_create_system(self, system_role: ProjectRole) -> None:
        assert system_role.name == "owner"
        assert system_role.is_system
        assert system_role.project_id is None
        assert system_role.permissions == ["project:read", "project:write"]

    def test_create_system_emits_event(self, system_role: ProjectRole) -> None:
        events = system_role.clear_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], ProjectRoleCreated)

    def test_create_custom(self, custom_role: ProjectRole) -> None:
        assert custom_role.name == "custom_role"
        assert not custom_role.is_system
        assert custom_role.project_id is not None
        assert custom_role.permissions == ["project:read"]

    def test_create_custom_emits_event(self, custom_role: ProjectRole) -> None:
        events = custom_role.clear_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], ProjectRoleCreated)


# ═══════════════════════════════════════════════════════════════════════════
# Обновление
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestProjectRoleUpdate:
    def test_update_permissions(self, custom_role: ProjectRole) -> None:
        custom_role.clear_domain_events()
        custom_role.update(permissions=["project:read", "project:write", "project:delete"])
        assert custom_role.permissions == ["project:read", "project:write", "project:delete"]

    def test_update_emits_event(self, custom_role: ProjectRole) -> None:
        custom_role.clear_domain_events()
        custom_role.update(permissions=["project:admin"])
        events = custom_role.clear_domain_events()
        assert any(isinstance(e, ProjectRoleUpdated) for e in events)

    def test_update_description(self, custom_role: ProjectRole) -> None:
        custom_role.update(description="New description")
        assert custom_role.description == "New description"


# ═══════════════════════════════════════════════════════════════════════════
# Удаление
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestProjectRoleDeletion:
    def test_can_be_deleted_custom(self, custom_role: ProjectRole) -> None:
        assert custom_role.can_be_deleted()

    def test_can_be_deleted_system(self, system_role: ProjectRole) -> None:
        assert not system_role.can_be_deleted()

    def test_assert_deletable_system_raises(self, system_role: ProjectRole) -> None:
        with pytest.raises(CannotDeleteSystemRoleException):
            system_role.assert_deletable()

    def test_mark_deleted_custom(self, custom_role: ProjectRole) -> None:
        custom_role.clear_domain_events()
        custom_role.mark_deleted()
        events = custom_role.clear_domain_events()
        assert any(isinstance(e, ProjectRoleDeleted) for e in events)

    def test_mark_deleted_system_raises(self, system_role: ProjectRole) -> None:
        with pytest.raises(CannotDeleteSystemRoleException):
            system_role.mark_deleted()

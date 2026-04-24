"""Unit-тесты для агрегата Department (Organization BC)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.domain.aggregates.department import Department
from app.context.organization.domain.events.department_events import (
    DepartmentCreated,
    DepartmentUpdated,
    DepartmentDeleted,
    DepartmentMemberAdded,
    DepartmentMemberRemoved,
)
from tests.factories import IdFactory


# ═══════════════════════════════════════════════════════════════════════════
# Создание
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestDepartmentCreation:
    def test_create(self, any_org_id: Id) -> None:
        dept = Department.create(org_id=any_org_id, name="Engineering")
        assert dept.name == "Engineering"
        assert dept.org_id == any_org_id
        assert dept.is_active is True
        assert dept.parent_id is None

    def test_create_with_parent(self, any_org_id: Id) -> None:
        parent_id = IdFactory()
        dept = Department.create(org_id=any_org_id, name="Backend", parent_id=parent_id)
        assert dept.parent_id == parent_id

    def test_create_with_lead(self, any_org_id: Id) -> None:
        lead_id = IdFactory()
        dept = Department.create(org_id=any_org_id, name="Engineering", lead_id=lead_id)
        assert dept.lead_id == lead_id

    def test_create_emits_department_created(self, new_department: Department) -> None:
        events = new_department.clear_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], DepartmentCreated)


# ═══════════════════════════════════════════════════════════════════════════
# Обновление
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestDepartmentUpdate:
    def test_update_name(self, department: Department) -> None:
        department.update(name="NewName")
        assert department.name == "NewName"

    def test_update_lead_id(self, department: Department) -> None:
        new_lead = IdFactory()
        department.update(lead_id=new_lead)
        assert department.lead_id == new_lead

    def test_update_emits_event(self, department: Department) -> None:
        department.update(name="NewName")
        events = department.clear_domain_events()
        assert any(isinstance(e, DepartmentUpdated) for e in events)

    def test_update_no_change_no_event(self, department: Department) -> None:
        department.update(name="Engineering")
        events = department.clear_domain_events()
        assert not any(isinstance(e, DepartmentUpdated) for e in events)


# ═══════════════════════════════════════════════════════════════════════════
# Участники
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestDepartmentMembers:
    def test_add_member(self, department: Department) -> None:
        user_id = IdFactory()
        department.add_member(user_id)
        assert user_id in department.member_ids

    def test_add_member_emits_event(self, department: Department) -> None:
        user_id = IdFactory()
        department.add_member(user_id)
        events = department.clear_domain_events()
        assert any(isinstance(e, DepartmentMemberAdded) for e in events)

    def test_add_duplicate_member_ignored(self, department: Department) -> None:
        user_id = IdFactory()
        department.add_member(user_id)
        department.clear_domain_events()
        department.add_member(user_id)
        events = department.clear_domain_events()
        assert not any(isinstance(e, DepartmentMemberAdded) for e in events)

    def test_remove_member(self, department: Department) -> None:
        user_id = IdFactory()
        department.add_member(user_id)
        department.clear_domain_events()
        department.remove_member(user_id)
        assert user_id not in department.member_ids

    def test_remove_member_emits_event(self, department: Department) -> None:
        user_id = IdFactory()
        department.add_member(user_id)
        department.clear_domain_events()
        department.remove_member(user_id)
        events = department.clear_domain_events()
        assert any(isinstance(e, DepartmentMemberRemoved) for e in events)

    def test_remove_nonexistent_member_ignored(self, department: Department) -> None:
        department.remove_member(IdFactory())
        events = department.clear_domain_events()
        assert not any(isinstance(e, DepartmentMemberRemoved) for e in events)


# ═══════════════════════════════════════════════════════════════════════════
# Статус
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestDepartmentStatus:
    def test_deactivate(self, department: Department) -> None:
        department.deactivate()
        assert department.is_active is False

    def test_deactivate_emits_department_deleted(self, department: Department) -> None:
        department.deactivate()
        events = department.clear_domain_events()
        assert any(isinstance(e, DepartmentDeleted) for e in events)

    def test_reactivate(self, department: Department) -> None:
        department.deactivate()
        department.clear_domain_events()
        department.reactivate()
        assert department.is_active is True

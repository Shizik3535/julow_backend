"""Unit-тесты для агрегата ProjectMembership (Project BC)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.domain.aggregates.project_membership import ProjectMembership
from app.context.project.domain.events.project_membership_events import (
    ProjectMemberJoined,
    ProjectMemberRemoved,
    ProjectMemberRoleChanged,
)
from app.context.project.domain.exceptions.project_membership_exceptions import (
    CannotRemoveOwnerAsMemberException,
    ProjectMemberNotFoundException,
)


# ═══════════════════════════════════════════════════════════════════════════
# Создание
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestProjectMembershipCreation:
    def test_create_with_owner(self, new_membership: ProjectMembership) -> None:
        assert len(new_membership.members) == 1
        assert new_membership.project_id is not None

    def test_create_emits_event(self, new_membership: ProjectMembership) -> None:
        events = new_membership.clear_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], ProjectMemberJoined)


# ═══════════════════════════════════════════════════════════════════════════
# Добавление участника
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestProjectMembershipAddMember:
    def test_add_member(self, membership: ProjectMembership, any_user_id: Id, any_role_id: Id) -> None:
        membership.add_member(user_id=any_user_id, role_id=any_role_id)
        assert len(membership.members) == 2

    def test_add_member_emits_event(self, membership: ProjectMembership, any_user_id: Id, any_role_id: Id) -> None:
        membership.add_member(user_id=any_user_id, role_id=any_role_id)
        events = membership.clear_domain_events()
        assert any(isinstance(e, ProjectMemberJoined) for e in events)

    def test_add_member_with_role(self, membership: ProjectMembership, any_user_id: Id, any_role_id: Id) -> None:
        membership.add_member(user_id=any_user_id, role_id=any_role_id)
        member = membership._find_member(any_user_id)
        assert member is not None
        assert member.role_id == any_role_id


# ═══════════════════════════════════════════════════════════════════════════
# Удаление участника
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestProjectMembershipRemoveMember:
    def test_remove_member(self, membership: ProjectMembership, any_user_id: Id, any_role_id: Id) -> None:
        membership.add_member(user_id=any_user_id, role_id=any_role_id)
        membership.clear_domain_events()
        membership.remove_member(user_id=any_user_id)
        assert len(membership.members) == 1

    def test_remove_member_emits_event(self, membership: ProjectMembership, any_user_id: Id, any_role_id: Id) -> None:
        membership.add_member(user_id=any_user_id, role_id=any_role_id)
        membership.clear_domain_events()
        membership.remove_member(user_id=any_user_id)
        events = membership.clear_domain_events()
        assert any(isinstance(e, ProjectMemberRemoved) for e in events)

    def test_remove_owner_raises(self, membership: ProjectMembership) -> None:
        owner_id = membership.members[0].user_id
        with pytest.raises(CannotRemoveOwnerAsMemberException):
            membership.remove_member(user_id=owner_id, is_owner=True)

    def test_remove_nonexistent_member_raises(self, membership: ProjectMembership) -> None:
        with pytest.raises(ProjectMemberNotFoundException):
            membership.remove_member(user_id=Id.generate())


# ═══════════════════════════════════════════════════════════════════════════
# Деактивация / реактивация
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestProjectMembershipDeactivateReactivate:
    def test_deactivate_member(self, membership: ProjectMembership, any_user_id: Id, any_role_id: Id) -> None:
        membership.add_member(user_id=any_user_id, role_id=any_role_id)
        membership.deactivate_member(user_id=any_user_id)
        member = membership._find_member(any_user_id)
        assert member is not None
        assert not member.is_active

    def test_deactivate_owner_raises(self, membership: ProjectMembership) -> None:
        owner_id = membership.members[0].user_id
        with pytest.raises(CannotRemoveOwnerAsMemberException):
            membership.deactivate_member(user_id=owner_id, is_owner=True)

    def test_reactivate_member(self, membership: ProjectMembership, any_user_id: Id, any_role_id: Id) -> None:
        membership.add_member(user_id=any_user_id, role_id=any_role_id)
        membership.deactivate_member(user_id=any_user_id)
        membership.reactivate_member(user_id=any_user_id)
        member = membership._find_member(any_user_id)
        assert member is not None
        assert member.is_active


# ═══════════════════════════════════════════════════════════════════════════
# Смена роли
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestProjectMembershipChangeRole:
    def test_change_member_role(self, membership: ProjectMembership, any_user_id: Id, any_role_id: Id) -> None:
        membership.add_member(user_id=any_user_id, role_id=any_role_id)
        membership.clear_domain_events()
        new_role_id = Id.generate()
        membership.change_member_role(user_id=any_user_id, new_role_id=new_role_id)
        member = membership._find_member(any_user_id)
        assert member is not None
        assert member.role_id == new_role_id

    def test_change_member_role_emits_event(self, membership: ProjectMembership, any_user_id: Id, any_role_id: Id) -> None:
        membership.add_member(user_id=any_user_id, role_id=any_role_id)
        membership.clear_domain_events()
        membership.change_member_role(user_id=any_user_id, new_role_id=Id.generate())
        events = membership.clear_domain_events()
        assert any(isinstance(e, ProjectMemberRoleChanged) for e in events)

    def test_change_role_nonexistent_member_raises(self, membership: ProjectMembership) -> None:
        with pytest.raises(ProjectMemberNotFoundException):
            membership.change_member_role(user_id=Id.generate(), new_role_id=Id.generate())

"""Unit-тесты для агрегата WorkspaceMembership (Workspace BC)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.domain.aggregates.workspace_membership import WorkspaceMembership
from app.context.workspace.domain.value_objects.member_source import MemberSource
from app.context.workspace.domain.events.workspace_membership_events import (
    WorkspaceMemberJoined,
    WorkspaceMemberDisplayNameChanged,
    WorkspaceMemberRoleChanged,
    WorkspaceMemberRemoved,
    WorkspaceMemberDeactivated,
    WorkspaceMemberReactivated,
    MemberAddedFromOrganization,
    MemberInheritedFromParent,
)
from app.context.workspace.domain.exceptions.workspace_membership_exceptions import (
    CannotRemoveOwnerAsMemberException,
    WorkspaceMemberNotFoundException,
)
from tests.factories import IdFactory


# ═══════════════════════════════════════════════════════════════════════════
# Создание
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestMembershipCreation:
    def test_create_with_owner(self, new_membership: WorkspaceMembership, any_owner_id: Id) -> None:
        assert len(new_membership.members) == 1
        assert new_membership.members[0].user_id == any_owner_id
        assert new_membership.members[0].source == MemberSource.DIRECT

    def test_create_emits_member_joined(self, new_membership: WorkspaceMembership) -> None:
        events = new_membership.clear_domain_events()
        assert any(isinstance(e, WorkspaceMemberJoined) for e in events)


# ═══════════════════════════════════════════════════════════════════════════
# Добавление участников
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAddMember:
    def test_add_member(self, membership: WorkspaceMembership) -> None:
        user_id = IdFactory()
        role_id = IdFactory()
        membership.add_member(user_id=user_id, role_id=role_id)
        assert len(membership.members) == 2

    def test_add_member_emits_joined(self, membership: WorkspaceMembership) -> None:
        user_id = IdFactory()
        role_id = IdFactory()
        membership.add_member(user_id=user_id, role_id=role_id)
        events = membership.clear_domain_events()
        event = next(e for e in events if isinstance(e, WorkspaceMemberJoined))
        assert event.user_id == str(user_id)

    def test_add_member_from_org(self, membership: WorkspaceMembership) -> None:
        user_id = IdFactory()
        role_id = IdFactory()
        membership.add_member_from_org(user_id=user_id, role_id=role_id)
        member = membership._find_member(user_id)
        assert member is not None
        assert member.source == MemberSource.ORGANIZATION

    def test_add_member_from_org_emits_event(self, membership: WorkspaceMembership) -> None:
        user_id = IdFactory()
        role_id = IdFactory()
        membership.add_member_from_org(user_id=user_id, role_id=role_id)
        events = membership.clear_domain_events()
        assert any(isinstance(e, MemberAddedFromOrganization) for e in events)

    def test_inherit_member_from_parent(self, membership: WorkspaceMembership) -> None:
        user_id = IdFactory()
        role_id = IdFactory()
        parent_id = IdFactory()
        membership.inherit_member_from_parent(
            user_id=user_id, role_id=role_id, parent_workspace_id=parent_id
        )
        member = membership._find_member(user_id)
        assert member is not None
        assert member.source == MemberSource.PARENT_WORKSPACE

    def test_inherit_member_emits_event(self, membership: WorkspaceMembership) -> None:
        user_id = IdFactory()
        role_id = IdFactory()
        parent_id = IdFactory()
        membership.inherit_member_from_parent(
            user_id=user_id, role_id=role_id, parent_workspace_id=parent_id
        )
        events = membership.clear_domain_events()
        assert any(isinstance(e, MemberInheritedFromParent) for e in events)


# ═══════════════════════════════════════════════════════════════════════════
# Удаление участников
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestRemoveMember:
    def test_remove_member(self, membership: WorkspaceMembership) -> None:
        user_id = IdFactory()
        role_id = IdFactory()
        membership.add_member(user_id=user_id, role_id=role_id)
        membership.clear_domain_events()
        membership.remove_member(user_id=user_id)
        assert membership._find_member(user_id) is None

    def test_remove_member_emits_removed(self, membership: WorkspaceMembership) -> None:
        user_id = IdFactory()
        role_id = IdFactory()
        membership.add_member(user_id=user_id, role_id=role_id)
        membership.clear_domain_events()
        membership.remove_member(user_id=user_id)
        events = membership.clear_domain_events()
        assert any(isinstance(e, WorkspaceMemberRemoved) for e in events)

    def test_remove_owner_raises(self, membership: WorkspaceMembership, any_owner_id: Id) -> None:
        with pytest.raises(CannotRemoveOwnerAsMemberException):
            membership.remove_member(user_id=any_owner_id, is_owner=True)

    def test_remove_nonexistent_member_raises(self, membership: WorkspaceMembership) -> None:
        with pytest.raises(WorkspaceMemberNotFoundException):
            membership.remove_member(user_id=IdFactory())


# ═══════════════════════════════════════════════════════════════════════════
# Деактивация / реактивация
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestDeactivateMember:
    def test_deactivate_member(self, membership: WorkspaceMembership) -> None:
        user_id = IdFactory()
        role_id = IdFactory()
        membership.add_member(user_id=user_id, role_id=role_id)
        membership.clear_domain_events()
        membership.deactivate_member(user_id=user_id)
        member = membership._get_member(user_id)
        assert member.is_active is False

    def test_deactivate_emits_event(self, membership: WorkspaceMembership) -> None:
        user_id = IdFactory()
        role_id = IdFactory()
        membership.add_member(user_id=user_id, role_id=role_id)
        membership.clear_domain_events()
        membership.deactivate_member(user_id=user_id)
        events = membership.clear_domain_events()
        assert any(isinstance(e, WorkspaceMemberDeactivated) for e in events)

    def test_deactivate_owner_raises(self, membership: WorkspaceMembership, any_owner_id: Id) -> None:
        with pytest.raises(CannotRemoveOwnerAsMemberException):
            membership.deactivate_member(user_id=any_owner_id, is_owner=True)

    def test_reactivate_member(self, membership: WorkspaceMembership) -> None:
        user_id = IdFactory()
        role_id = IdFactory()
        membership.add_member(user_id=user_id, role_id=role_id)
        membership.deactivate_member(user_id=user_id)
        membership.clear_domain_events()
        membership.reactivate_member(user_id=user_id)
        member = membership._get_member(user_id)
        assert member.is_active is True

    def test_reactivate_emits_event(self, membership: WorkspaceMembership) -> None:
        user_id = IdFactory()
        role_id = IdFactory()
        membership.add_member(user_id=user_id, role_id=role_id)
        membership.deactivate_member(user_id=user_id)
        membership.clear_domain_events()
        membership.reactivate_member(user_id=user_id)
        events = membership.clear_domain_events()
        assert any(isinstance(e, WorkspaceMemberReactivated) for e in events)


# ═══════════════════════════════════════════════════════════════════════════
# Смена роли
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestChangeMemberRole:
    def test_change_member_role(self, membership: WorkspaceMembership) -> None:
        user_id = IdFactory()
        role_id = IdFactory()
        membership.add_member(user_id=user_id, role_id=role_id)
        membership.clear_domain_events()
        new_role = IdFactory()
        membership.change_member_role(user_id=user_id, new_role_id=new_role)
        member = membership._get_member(user_id)
        assert member.role_id == new_role

    def test_change_role_emits_event(self, membership: WorkspaceMembership) -> None:
        user_id = IdFactory()
        role_id = IdFactory()
        membership.add_member(user_id=user_id, role_id=role_id)
        membership.clear_domain_events()
        new_role = IdFactory()
        membership.change_member_role(user_id=user_id, new_role_id=new_role)
        events = membership.clear_domain_events()
        assert any(isinstance(e, WorkspaceMemberRoleChanged) for e in events)

    def test_change_role_nonexistent_raises(self, membership: WorkspaceMembership) -> None:
        with pytest.raises(WorkspaceMemberNotFoundException):
            membership.change_member_role(user_id=IdFactory(), new_role_id=IdFactory())


# ═══════════════════════════════════════════════════════════════════════════
# Обновление отображаемого имени
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestUpdateDisplayName:
    def test_update_display_name(self, membership: WorkspaceMembership) -> None:
        user_id = IdFactory()
        role_id = IdFactory()
        membership.add_member(user_id=user_id, role_id=role_id)
        membership.clear_domain_events()
        membership.update_member_display_name(user_id=user_id, display_name="Alice")
        member = membership._get_member(user_id)
        assert member.display_name == "Alice"

    def test_update_display_name_emits_event(self, membership: WorkspaceMembership) -> None:
        user_id = IdFactory()
        role_id = IdFactory()
        membership.add_member(user_id=user_id, role_id=role_id)
        membership.clear_domain_events()
        membership.update_member_display_name(user_id=user_id, display_name="Alice")
        events = membership.clear_domain_events()
        assert any(isinstance(e, WorkspaceMemberDisplayNameChanged) for e in events)

    def test_update_display_name_nonexistent_raises(self, membership: WorkspaceMembership) -> None:
        with pytest.raises(WorkspaceMemberNotFoundException):
            membership.update_member_display_name(user_id=IdFactory(), display_name="Alice")

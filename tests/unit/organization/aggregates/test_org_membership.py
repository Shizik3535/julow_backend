"""Unit-тесты для агрегата OrgMembership (Organization BC)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.domain.aggregates.org_membership import OrgMembership
from app.context.organization.domain.events.org_membership_events import (
    OrgMemberJoined,
    OrgMemberDisplayNameChanged,
    OrgMemberRoleChanged,
    OrgMemberRemoved,
    OrgMemberDeactivated,
    OrgMemberReactivated,
)
from app.context.organization.domain.exceptions.org_membership_exceptions import (
    CannotRemoveOwnerAsMemberException,
    OrgMemberNotFoundException,
)
from tests.factories import IdFactory


# ═══════════════════════════════════════════════════════════════════════════
# Создание
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestOrgMembershipCreation:
    def test_create_with_owner(self, new_membership: OrgMembership, any_owner_id: Id) -> None:
        assert len(new_membership.members) == 1
        assert new_membership.members[0].user_id == any_owner_id

    def test_create_emits_member_joined(self, new_membership: OrgMembership) -> None:
        events = new_membership.clear_domain_events()
        assert any(isinstance(e, OrgMemberJoined) for e in events)


# ═══════════════════════════════════════════════════════════════════════════
# Добавление участника
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestOrgMembershipAddMember:
    def test_add_member(self, membership: OrgMembership) -> None:
        user_id = IdFactory()
        role_id = IdFactory()
        membership.add_member(user_id=user_id, role_id=role_id)
        assert len(membership.members) == 2

    def test_add_member_emits_event(self, membership: OrgMembership) -> None:
        user_id = IdFactory()
        role_id = IdFactory()
        membership.add_member(user_id=user_id, role_id=role_id)
        events = membership.clear_domain_events()
        assert any(isinstance(e, OrgMemberJoined) for e in events)


# ═══════════════════════════════════════════════════════════════════════════
# Удаление участника
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestOrgMembershipRemoveMember:
    def test_remove_member(self, membership: OrgMembership) -> None:
        user_id = IdFactory()
        role_id = IdFactory()
        membership.add_member(user_id=user_id, role_id=role_id)
        membership.clear_domain_events()
        membership.remove_member(user_id)
        assert len(membership.members) == 1

    def test_remove_member_emits_event(self, membership: OrgMembership) -> None:
        user_id = IdFactory()
        role_id = IdFactory()
        membership.add_member(user_id=user_id, role_id=role_id)
        membership.clear_domain_events()
        membership.remove_member(user_id)
        events = membership.clear_domain_events()
        assert any(isinstance(e, OrgMemberRemoved) for e in events)

    def test_remove_member_owner_raises(self, membership: OrgMembership, any_owner_id: Id) -> None:
        with pytest.raises(CannotRemoveOwnerAsMemberException):
            membership.remove_member(any_owner_id, is_owner=True)

    def test_remove_nonexistent_member_raises(self, membership: OrgMembership) -> None:
        with pytest.raises(OrgMemberNotFoundException):
            membership.remove_member(IdFactory())


# ═══════════════════════════════════════════════════════════════════════════
# Деактивация
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestOrgMembershipDeactivateMember:
    def test_deactivate_member(self, membership: OrgMembership) -> None:
        user_id = IdFactory()
        role_id = IdFactory()
        membership.add_member(user_id=user_id, role_id=role_id)
        membership.clear_domain_events()
        membership.deactivate_member(user_id)
        member = membership._find_member(user_id)
        assert member is not None
        assert member.is_active is False

    def test_deactivate_member_emits_event(self, membership: OrgMembership) -> None:
        user_id = IdFactory()
        role_id = IdFactory()
        membership.add_member(user_id=user_id, role_id=role_id)
        membership.clear_domain_events()
        membership.deactivate_member(user_id)
        events = membership.clear_domain_events()
        assert any(isinstance(e, OrgMemberDeactivated) for e in events)

    def test_deactivate_owner_raises(self, membership: OrgMembership, any_owner_id: Id) -> None:
        with pytest.raises(CannotRemoveOwnerAsMemberException):
            membership.deactivate_member(any_owner_id, is_owner=True)


# ═══════════════════════════════════════════════════════════════════════════
# Реактивация
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestOrgMembershipReactivateMember:
    def test_reactivate_member(self, membership: OrgMembership) -> None:
        user_id = IdFactory()
        role_id = IdFactory()
        membership.add_member(user_id=user_id, role_id=role_id)
        membership.deactivate_member(user_id)
        membership.clear_domain_events()
        membership.reactivate_member(user_id)
        member = membership._find_member(user_id)
        assert member is not None
        assert member.is_active is True

    def test_reactivate_member_emits_event(self, membership: OrgMembership) -> None:
        user_id = IdFactory()
        role_id = IdFactory()
        membership.add_member(user_id=user_id, role_id=role_id)
        membership.deactivate_member(user_id)
        membership.clear_domain_events()
        membership.reactivate_member(user_id)
        events = membership.clear_domain_events()
        assert any(isinstance(e, OrgMemberReactivated) for e in events)


# ═══════════════════════════════════════════════════════════════════════════
# Смена роли
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestOrgMembershipChangeRole:
    def test_change_member_role(self, membership: OrgMembership) -> None:
        user_id = IdFactory()
        role_id = IdFactory()
        membership.add_member(user_id=user_id, role_id=role_id)
        membership.clear_domain_events()
        new_role_id = IdFactory()
        membership.change_member_role(user_id, new_role_id)
        member = membership._find_member(user_id)
        assert member is not None
        assert member.role_id == new_role_id

    def test_change_member_role_emits_event(self, membership: OrgMembership) -> None:
        user_id = IdFactory()
        role_id = IdFactory()
        membership.add_member(user_id=user_id, role_id=role_id)
        membership.clear_domain_events()
        membership.change_member_role(user_id, IdFactory())
        events = membership.clear_domain_events()
        assert any(isinstance(e, OrgMemberRoleChanged) for e in events)


# ═══════════════════════════════════════════════════════════════════════════
# Отображаемое имя
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestOrgMembershipDisplayName:
    def test_update_member_display_name(self, membership: OrgMembership) -> None:
        user_id = IdFactory()
        role_id = IdFactory()
        membership.add_member(user_id=user_id, role_id=role_id)
        membership.clear_domain_events()
        membership.update_member_display_name(user_id, "Alice")
        member = membership._find_member(user_id)
        assert member is not None
        assert member.display_name == "Alice"

    def test_update_member_display_name_emits_event(self, membership: OrgMembership) -> None:
        user_id = IdFactory()
        role_id = IdFactory()
        membership.add_member(user_id=user_id, role_id=role_id)
        membership.clear_domain_events()
        membership.update_member_display_name(user_id, "Alice")
        events = membership.clear_domain_events()
        assert any(isinstance(e, OrgMemberDisplayNameChanged) for e in events)

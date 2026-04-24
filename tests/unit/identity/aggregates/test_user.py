"""Unit-тесты для агрегата User (Identity BC)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.identity.domain.aggregates.user import User
from app.context.identity.domain.events.user_events import (
    AccountDeletionRequested,
    AccountDisabled,
    AccountReactivated,
    EmailConfirmed,
    RoleAssigned,
    RoleRemoved,
    UserRegistered,
)
from app.context.identity.domain.exceptions.user_exceptions import (
    AccountDeletionPendingException,
    DuplicateRoleException,
    LastSystemRoleException,
)
from app.context.identity.domain.value_objects.account_status import AccountStatus


# ═══════════════════════════════════════════════════════════════════════════
# Регистрация
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestUserRegistration:
    def test_register_user(self, pending_user: User) -> None:
        user = pending_user
        assert user.status == AccountStatus.PENDING_VERIFICATION
        assert not user.is_email_confirmed

    def test_register_emits_event(self, pending_user: User) -> None:
        user = pending_user
        events = user.clear_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], UserRegistered)


# ═══════════════════════════════════════════════════════════════════════════
# Email верификация
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestUserEmailConfirmation:
    def test_confirm_email(self, pending_user: User) -> None:
        user = pending_user
        user.confirm_email()
        assert user.is_email_confirmed
        assert user.status == AccountStatus.ACTIVE

    def test_confirm_email_emits_event(self, pending_user: User) -> None:
        user = pending_user
        user.clear_domain_events()
        user.confirm_email()
        events = user.clear_domain_events()
        assert any(isinstance(e, EmailConfirmed) for e in events)

    def test_confirm_email_already_confirmed_is_noop(self, active_user: User) -> None:
        user = active_user
        user.confirm_email()
        assert user.is_email_confirmed


# ═══════════════════════════════════════════════════════════════════════════
# Роли
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestUserRoles:
    def test_assign_role(self, active_user: User) -> None:
        user = active_user
        role_id = Id.generate()
        user.assign_role(role_id)
        assert role_id in user.role_ids

    def test_assign_role_emits_event(self, active_user: User) -> None:
        user = active_user
        role_id = Id.generate()
        user.assign_role(role_id)
        events = user.clear_domain_events()
        assert any(isinstance(e, RoleAssigned) for e in events)

    def test_assign_duplicate_role_raises(self, active_user: User) -> None:
        user = active_user
        role_id = Id.generate()
        user.assign_role(role_id)
        with pytest.raises(DuplicateRoleException):
            user.assign_role(role_id)

    def test_remove_role(self, active_user: User) -> None:
        user = active_user
        role_id = Id.generate()
        user.assign_role(role_id)
        user.remove_role(role_id, is_system_role=False)
        assert role_id not in user.role_ids

    def test_remove_role_emits_event(self, active_user: User) -> None:
        user = active_user
        role_id = Id.generate()
        user.assign_role(role_id)
        user.clear_domain_events()
        user.remove_role(role_id, is_system_role=False)
        events = user.clear_domain_events()
        assert any(isinstance(e, RoleRemoved) for e in events)

    def test_remove_last_system_role_raises(self, active_user: User) -> None:
        user = active_user
        role_id = Id.generate()
        user.assign_role(role_id)
        with pytest.raises(LastSystemRoleException):
            user.remove_role(role_id, is_system_role=True)

    def test_remove_nonexistent_role_ignored(self, active_user: User) -> None:
        user = active_user
        user.clear_domain_events()
        user.remove_role(Id.generate(), is_system_role=False)
        events = user.clear_domain_events()
        assert not any(isinstance(e, RoleRemoved) for e in events)


# ═══════════════════════════════════════════════════════════════════════════
# Статус
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestUserStatus:
    def test_disable_account(self, active_user: User) -> None:
        user = active_user
        user.disable()
        assert user.status == AccountStatus.DISABLED

    def test_disable_emits_event(self, active_user: User) -> None:
        user = active_user
        user.clear_domain_events()
        user.disable()
        events = user.clear_domain_events()
        assert any(isinstance(e, AccountDisabled) for e in events)

    def test_reactivate_account(self, active_user: User) -> None:
        user = active_user
        user.disable()
        user.reactivate()
        assert user.status == AccountStatus.ACTIVE

    def test_reactivate_emits_event(self, active_user: User) -> None:
        user = active_user
        user.disable()
        user.clear_domain_events()
        user.reactivate()
        events = user.clear_domain_events()
        assert any(isinstance(e, AccountReactivated) for e in events)

    def test_reactivate_without_email_confirmed_sets_pending(self, pending_user: User) -> None:
        user = pending_user
        user.status = AccountStatus.DISABLED
        user.reactivate()
        assert user.status == AccountStatus.PENDING_VERIFICATION

    def test_request_account_deletion(self, active_user: User) -> None:
        user = active_user
        user.request_account_deletion()
        assert user.status == AccountStatus.PENDING_DELETION

    def test_request_deletion_emits_event(self, active_user: User) -> None:
        user = active_user
        user.clear_domain_events()
        user.request_account_deletion()
        events = user.clear_domain_events()
        assert any(isinstance(e, AccountDeletionRequested) for e in events)

    def test_operations_blocked_when_pending_deletion(self, active_user: User) -> None:
        user = active_user
        user.request_account_deletion()
        with pytest.raises(AccountDeletionPendingException):
            user.assign_role(Id.generate())

    def test_cancel_account_deletion(self, active_user: User) -> None:
        user = active_user
        user.request_account_deletion()
        user.cancel_account_deletion()
        assert user.status == AccountStatus.ACTIVE

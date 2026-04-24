from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_aggregate import AggregateRoot
from app.shared.domain.value_objects.email_vo import Email
from app.shared.domain.value_objects.id_vo import Id
from app.context.identity.domain.events.user_events import (
    AccountDeletionRequested,
    AccountDisabled,
    AccountReactivated,
    EmailConfirmed,
    PasswordChanged,
    RoleAssigned,
    RoleRemoved,
    UserRegistered,
)
from app.context.identity.domain.exceptions.user_exceptions import (
    AccountDeletionPendingException,
    AccountNotDisabledException,
    AccountNotPendingDeletionException,
    DuplicateRoleException,
    EmailNotConfirmedException,
    LastSystemRoleException,
)
from app.context.identity.domain.value_objects.account_status import AccountStatus
from app.context.identity.domain.value_objects.auth_provider import AuthProvider


@dataclass
class User(AggregateRoot):
    """
    Корень агрегата пользователя (Identity BC).

    Отвечает за идентичность, статус и роли.
    Не управляет аутентификацией напрямую — делегирует UserAuth.

    Атрибуты:
        email: Email-адрес пользователя.
        status: Статус аккаунта.
        role_ids: Список ID ролей (opaque ID).
        is_email_confirmed: Подтверждён ли email.
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    email: Email = field(default_factory=lambda: Email("user@example.com"))
    status: AccountStatus = AccountStatus.PENDING_VERIFICATION
    role_ids: list[Id] = field(default_factory=list)
    is_email_confirmed: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    # --- Фабричные методы ---

    @classmethod
    def register(cls, email: Email, auth_provider: AuthProvider) -> User:
        """Создаёт пользователя. Статус: PENDING_VERIFICATION."""
        user = cls(
            email=email,
            status=AccountStatus.PENDING_VERIFICATION,
            is_email_confirmed=False,
        )
        user._register_event(
            UserRegistered(
                user_id=str(user.id),
                email=email.value,
                auth_provider=auth_provider,
            )
        )
        return user

    # --- Email верификация ---

    def confirm_email(self) -> None:
        """Подтверждает email пользователя."""
        self._assert_not_pending_deletion()
        if self.is_email_confirmed:
            return
        self.is_email_confirmed = True
        if self.status == AccountStatus.PENDING_VERIFICATION:
            self.status = AccountStatus.ACTIVE
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            EmailConfirmed(user_id=str(self.id))
        )

    # --- Роли ---

    def assign_role(self, role_id: Id) -> None:
        """Назначает роль пользователю."""
        self._assert_not_pending_deletion()
        if role_id in self.role_ids:
            raise DuplicateRoleException()
        self.role_ids.append(role_id)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            RoleAssigned(user_id=str(self.id), role_id=str(role_id))
        )

    def remove_role(self, role_id: Id, is_system_role: bool = True) -> None:
        """Снимает роль с пользователя."""
        self._assert_not_pending_deletion()
        if role_id not in self.role_ids:
            return
        if is_system_role:
            system_role_ids = [rid for rid in self.role_ids if rid != role_id]
            if len(system_role_ids) == 0:
                raise LastSystemRoleException()
        self.role_ids.remove(role_id)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            RoleRemoved(user_id=str(self.id), role_id=str(role_id))
        )

    # --- Статус аккаунта ---

    def disable(self) -> None:
        """Деактивирует аккаунт."""
        self._assert_not_pending_deletion()
        self.status = AccountStatus.DISABLED
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            AccountDisabled(user_id=str(self.id))
        )

    def reactivate(self) -> None:
        """Реактивирует аккаунт."""
        self._assert_not_pending_deletion()
        if self.status != AccountStatus.DISABLED:
            raise AccountNotDisabledException()
        self.status = AccountStatus.ACTIVE if self.is_email_confirmed else AccountStatus.PENDING_VERIFICATION
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            AccountReactivated(user_id=str(self.id))
        )

    def request_account_deletion(self) -> None:
        """Запрашивает удаление аккаунта."""
        self._assert_not_pending_deletion()
        self.status = AccountStatus.PENDING_DELETION
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            AccountDeletionRequested(user_id=str(self.id))
        )

    def cancel_account_deletion(self) -> None:
        """Отменяет удаление аккаунта."""
        if self.status != AccountStatus.PENDING_DELETION:
            raise AccountNotPendingDeletionException()
        self.status = AccountStatus.ACTIVE if self.is_email_confirmed else AccountStatus.PENDING_VERIFICATION
        self.updated_at = datetime.now(tz=timezone.utc)

    # --- Приватные методы ---

    def _assert_not_pending_deletion(self) -> None:
        """Проверяет, что аккаунт не в процессе удаления."""
        if self.status == AccountStatus.PENDING_DELETION:
            raise AccountDeletionPendingException()

from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_domain_event import BaseDomainEvent
from app.context.identity.domain.value_objects.auth_provider import AuthProvider


@dataclass(frozen=True)
class UserRegistered(BaseDomainEvent):
    """Пользователь зарегистрирован."""

    user_id: str = ""
    email: str = ""
    auth_provider: AuthProvider = AuthProvider.EMAIL_PASSWORD


@dataclass(frozen=True)
class EmailConfirmed(BaseDomainEvent):
    """Email подтверждён."""

    user_id: str = ""


@dataclass(frozen=True)
class RoleAssigned(BaseDomainEvent):
    """Роль назначена пользователю."""

    user_id: str = ""
    role_id: str = ""


@dataclass(frozen=True)
class RoleRemoved(BaseDomainEvent):
    """Роль снята с пользователя."""

    user_id: str = ""
    role_id: str = ""


@dataclass(frozen=True)
class PasswordChanged(BaseDomainEvent):
    """Пароль изменён."""

    user_id: str = ""


@dataclass(frozen=True)
class AccountDeletionRequested(BaseDomainEvent):
    """Запрос удаления аккаунта."""

    user_id: str = ""


@dataclass(frozen=True)
class AccountDeletionCancelled(BaseDomainEvent):
    """Отмена запроса удаления аккаунта."""

    user_id: str = ""


@dataclass(frozen=True)
class AccountDisabled(BaseDomainEvent):
    """Аккаунт деактивирован."""

    user_id: str = ""


@dataclass(frozen=True)
class AccountReactivated(BaseDomainEvent):
    """Аккаунт реактивирован."""

    user_id: str = ""


@dataclass(frozen=True)
class UserDeleted(BaseDomainEvent):
    """Пользователь удалён (окончательно, после grace period)."""

    user_id: str = ""

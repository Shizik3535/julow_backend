from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_domain_event import BaseDomainEvent
from app.context.identity.domain.value_objects.auth_provider import AuthProvider
from app.context.identity.domain.value_objects.two_factor_method import TwoFactorMethod


@dataclass(frozen=True)
class UserLoggedIn(BaseDomainEvent):
    """Успешный вход пользователя."""

    user_id: str = ""
    session_id: str = ""
    ip: str = ""
    device: str = ""


@dataclass(frozen=True)
class LoginFailed(BaseDomainEvent):
    """Неудачная попытка входа."""

    user_id: str = ""
    ip: str = ""


@dataclass(frozen=True)
class UserLockedOut(BaseDomainEvent):
    """Блокировка после неудачных попыток."""

    user_id: str = ""
    lockout_until: str = ""


@dataclass(frozen=True)
class AuthFactorEnabled(BaseDomainEvent):
    """Фактор 2FA включён."""

    user_id: str = ""
    method: TwoFactorMethod = TwoFactorMethod.TOTP
    is_primary: bool = False


@dataclass(frozen=True)
class AuthFactorDisabled(BaseDomainEvent):
    """Фактор 2FA отключён."""

    user_id: str = ""
    method: TwoFactorMethod = TwoFactorMethod.TOTP


@dataclass(frozen=True)
class NewDeviceLogin(BaseDomainEvent):
    """Вход с нового устройства/IP."""

    user_id: str = ""
    ip: str = ""
    device: str = ""


@dataclass(frozen=True)
class PasswordResetRequested(BaseDomainEvent):
    """Запрос сброса пароля."""

    user_id: str = ""
    email: str = ""


@dataclass(frozen=True)
class PasswordResetCompleted(BaseDomainEvent):
    """Пароль сброшен."""

    user_id: str = ""


@dataclass(frozen=True)
class OAuthLinked(BaseDomainEvent):
    """OAuth-аккаунт привязан."""

    user_id: str = ""
    provider: AuthProvider = AuthProvider.OAUTH_GOOGLE


@dataclass(frozen=True)
class OAuthUnlinked(BaseDomainEvent):
    """OAuth-аккаунт отвязан."""

    user_id: str = ""
    provider: AuthProvider = AuthProvider.OAUTH_GOOGLE


@dataclass(frozen=True)
class SSOLinked(BaseDomainEvent):
    """SSO привязан."""

    user_id: str = ""


@dataclass(frozen=True)
class SSOUserProvisioned(BaseDomainEvent):
    """Пользователь зарегистрирован через SSO — требуется auto-provision в организацию."""

    user_id: str = ""
    org_id: str = ""
    email: str = ""
    default_role_id: str = ""


@dataclass(frozen=True)
class TrustedDeviceAdded(BaseDomainEvent):
    """Доверенное устройство добавлено."""

    user_id: str = ""
    device_fingerprint: str = ""


@dataclass(frozen=True)
class TrustedDeviceRemoved(BaseDomainEvent):
    """Доверенное устройство удалено."""

    user_id: str = ""
    device_fingerprint: str = ""

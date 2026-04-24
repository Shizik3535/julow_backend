"""
Identity BC conftest — фикстуры для unit-тестов Identity BC.

Содержит фабричные фикстуры для агрегатов, VOs и политик,
используемых в нескольких тестовых модулях.
"""

import pytest

from app.shared.domain.value_objects.email_vo import Email
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.ip_address_vo import IpAddress
from app.context.identity.domain.aggregates.session import Session
from app.context.identity.domain.aggregates.user import User
from app.context.identity.domain.aggregates.user_auth import UserAuth
from app.context.identity.domain.value_objects.auth_provider import AuthProvider
from app.context.identity.domain.value_objects.device_info import DeviceInfo
from app.context.identity.domain.value_objects.failed_login_policy import FailedLoginPolicy
from app.context.identity.domain.value_objects.lockout_threshold import LockoutThreshold
from app.context.identity.domain.value_objects.password_hash import PasswordHash
from app.context.identity.domain.value_objects.refresh_token import RefreshToken
from app.context.identity.domain.value_objects.two_fa_secret import TwoFASecret
from app.context.identity.domain.value_objects.two_factor_method import TwoFactorMethod
from tests.factories import EmailFactory, IdFactory, PasswordHashFactory, RefreshTokenFactory


# ── Value Object фикстуры ─────────────────────────────────────────────────


@pytest.fixture
def any_email() -> Email:
    """Случайный Email."""
    return EmailFactory()


@pytest.fixture
def any_password_hash() -> PasswordHash:
    """Случайный PasswordHash."""
    return PasswordHashFactory()


@pytest.fixture
def any_ip() -> IpAddress:
    """IP-адрес по умолчанию."""
    return IpAddress("192.168.1.1")


@pytest.fixture
def any_device_info() -> DeviceInfo:
    """DeviceInfo по умолчанию."""
    return DeviceInfo(user_agent="Mozilla/5.0", os="Windows", browser="Chrome")


@pytest.fixture
def any_refresh_token() -> RefreshToken:
    """Случайный RefreshToken."""
    return RefreshTokenFactory()


@pytest.fixture
def any_totp_secret() -> TwoFASecret:
    """Секрет TOTP по умолчанию."""
    return TwoFASecret(value="JBSWY3DPEHPK3PXP", method=TwoFactorMethod.TOTP)


# ── Политики ──────────────────────────────────────────────────────────────


@pytest.fixture
def default_lockout_policy() -> FailedLoginPolicy:
    """Политика блокировки: 3 попытки → 15 мин, 5 попыток → 60 мин."""
    return FailedLoginPolicy(thresholds=[
        LockoutThreshold(failed_attempts=3, lock_duration_minutes=15),
        LockoutThreshold(failed_attempts=5, lock_duration_minutes=60),
    ])


# ── Агрегат User ──────────────────────────────────────────────────────────


@pytest.fixture
def pending_user(any_email: Email) -> User:
    """Пользователь со статусом PENDING_VERIFICATION."""
    user = User.register(any_email, AuthProvider.EMAIL_PASSWORD)
    return user


@pytest.fixture
def active_user(pending_user: User) -> User:
    """Пользователь со статусом ACTIVE (email подтверждён)."""
    pending_user.confirm_email()
    pending_user.clear_domain_events()
    return pending_user


# ── Агрегат UserAuth ──────────────────────────────────────────────────────


@pytest.fixture
def email_user_auth(any_email: Email, any_password_hash: PasswordHash) -> UserAuth:
    """UserAuth для регистрации по email + пароль."""
    user_id = Id.generate()
    return UserAuth.create_for_email_auth(user_id, any_email, any_password_hash)


@pytest.fixture
def oauth_user_auth(any_email: Email) -> UserAuth:
    """UserAuth для регистрации через OAuth Google."""
    user_id = Id.generate()
    return UserAuth.create_for_oauth(user_id, any_email, AuthProvider.OAUTH_GOOGLE, "google_123")


# ── Агрегат Session ───────────────────────────────────────────────────────


@pytest.fixture
def active_session(any_device_info: DeviceInfo, any_ip: IpAddress, any_refresh_token: RefreshToken) -> Session:
    """Активная сессия."""
    return Session.create(
        user_id=IdFactory(),
        device_info=any_device_info,
        ip_address=any_ip,
        is_remember_me=False,
        refresh_token=any_refresh_token,
    )

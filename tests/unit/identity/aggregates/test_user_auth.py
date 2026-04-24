"""Unit-тесты для агрегата UserAuth (Identity BC)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.ip_address_vo import IpAddress
from app.context.identity.domain.aggregates.user_auth import UserAuth
from app.context.identity.domain.events.auth_events import (
    AuthFactorDisabled,
    AuthFactorEnabled,
    LoginFailed,
    NewDeviceLogin,
    OAuthLinked,
    OAuthUnlinked,
    TrustedDeviceAdded,
    UserLockedOut,
    UserLoggedIn,
)
from app.context.identity.domain.events.user_events import PasswordChanged
from app.context.identity.domain.exceptions.user_exceptions import (
    CannotUnlinkLastProviderException,
    InvalidBackupCodeException,
)
from app.context.identity.domain.exceptions.auth_exceptions import (
    OAuthProviderAlreadyLinkedException,
)
from app.context.identity.domain.value_objects.auth_provider import AuthProvider
from app.context.identity.domain.value_objects.device_info import DeviceInfo
from app.context.identity.domain.value_objects.failed_login_policy import FailedLoginPolicy
from app.context.identity.domain.value_objects.lockout_threshold import LockoutThreshold
from app.context.identity.domain.value_objects.password_hash import PasswordHash
from app.context.identity.domain.value_objects.two_fa_secret import TwoFASecret
from app.context.identity.domain.value_objects.two_factor_method import TwoFactorMethod


# ═══════════════════════════════════════════════════════════════════════════
# Создание
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestUserAuthCreation:
    def test_create_for_email_auth(self, email_user_auth: UserAuth) -> None:
        auth = email_user_auth
        assert auth.password_hash is not None
        assert len(auth.oauth_links) == 0

    def test_create_for_oauth(self, oauth_user_auth: UserAuth) -> None:
        auth = oauth_user_auth
        assert auth.password_hash is None
        assert len(auth.oauth_links) == 1
        assert auth.oauth_links[0].provider == AuthProvider.OAUTH_GOOGLE

    def test_create_for_oauth_emits_event(self, oauth_user_auth: UserAuth) -> None:
        auth = oauth_user_auth
        events = auth.clear_domain_events()
        assert any(isinstance(e, OAuthLinked) for e in events)


# ═══════════════════════════════════════════════════════════════════════════
# Блокировка
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestUserAuthLockout:
    def test_record_failed_login(self, email_user_auth: UserAuth, default_lockout_policy: FailedLoginPolicy) -> None:
        auth = email_user_auth
        auth.record_failed_login(default_lockout_policy)
        assert auth.failed_login_attempts == 1

    def test_record_failed_login_emits_event(self, email_user_auth: UserAuth, default_lockout_policy: FailedLoginPolicy) -> None:
        auth = email_user_auth
        auth.clear_domain_events()
        auth.record_failed_login(default_lockout_policy)
        events = auth.clear_domain_events()
        assert any(isinstance(e, LoginFailed) for e in events)

    def test_lock_after_threshold(self, email_user_auth: UserAuth, default_lockout_policy: FailedLoginPolicy) -> None:
        auth = email_user_auth
        for _ in range(3):
            auth.record_failed_login(default_lockout_policy)
        assert auth.locked_until is not None

    def test_lock_emits_event(self, email_user_auth: UserAuth, default_lockout_policy: FailedLoginPolicy) -> None:
        auth = email_user_auth
        for _ in range(2):
            auth.record_failed_login(default_lockout_policy)
        auth.clear_domain_events()
        auth.record_failed_login(default_lockout_policy)
        events = auth.clear_domain_events()
        assert any(isinstance(e, UserLockedOut) for e in events)

    def test_is_locked(self, email_user_auth: UserAuth, default_lockout_policy: FailedLoginPolicy) -> None:
        auth = email_user_auth
        for _ in range(3):
            auth.record_failed_login(default_lockout_policy)
        assert auth.is_locked()

    def test_unlock(self, email_user_auth: UserAuth, default_lockout_policy: FailedLoginPolicy) -> None:
        auth = email_user_auth
        for _ in range(3):
            auth.record_failed_login(default_lockout_policy)
        auth.unlock()
        assert not auth.is_locked()
        assert auth.failed_login_attempts == 0


# ═══════════════════════════════════════════════════════════════════════════
# 2FA
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestUserAuth2FA:
    def test_enable_auth_factor(self, email_user_auth: UserAuth, any_totp_secret: TwoFASecret) -> None:
        auth = email_user_auth
        auth.enable_auth_factor(TwoFactorMethod.TOTP, any_totp_secret)
        assert len(auth.auth_factors) == 1
        assert auth.auth_factors[0].is_enabled

    def test_enable_auth_factor_emits_event(self, email_user_auth: UserAuth, any_totp_secret: TwoFASecret) -> None:
        auth = email_user_auth
        auth.clear_domain_events()
        auth.enable_auth_factor(TwoFactorMethod.TOTP, any_totp_secret)
        events = auth.clear_domain_events()
        assert any(isinstance(e, AuthFactorEnabled) for e in events)

    def test_disable_auth_factor(self, email_user_auth: UserAuth, any_totp_secret: TwoFASecret) -> None:
        auth = email_user_auth
        auth.enable_auth_factor(TwoFactorMethod.TOTP, any_totp_secret)
        auth.disable_auth_factor(TwoFactorMethod.TOTP)
        assert not auth.auth_factors[0].is_enabled

    def test_disable_auth_factor_emits_event(self, email_user_auth: UserAuth, any_totp_secret: TwoFASecret) -> None:
        auth = email_user_auth
        auth.enable_auth_factor(TwoFactorMethod.TOTP, any_totp_secret)
        auth.clear_domain_events()
        auth.disable_auth_factor(TwoFactorMethod.TOTP)
        events = auth.clear_domain_events()
        assert any(isinstance(e, AuthFactorDisabled) for e in events)


# ═══════════════════════════════════════════════════════════════════════════
# Резервные коды
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestUserAuthBackupCodes:
    def test_generate_backup_codes(self, email_user_auth: UserAuth, any_totp_secret: TwoFASecret) -> None:
        auth = email_user_auth
        auth.enable_auth_factor(TwoFactorMethod.TOTP, any_totp_secret)
        auth.generate_backup_codes(["hash1", "hash2", "hash3"])
        assert len(auth.backup_codes) == 3

    def test_use_backup_code(self, email_user_auth: UserAuth, any_totp_secret: TwoFASecret) -> None:
        auth = email_user_auth
        auth.enable_auth_factor(TwoFactorMethod.TOTP, any_totp_secret)
        auth.generate_backup_codes(["hash1", "hash2"])
        auth.use_backup_code("hash1", lambda plain, stored: plain == stored)
        assert auth.backup_codes[0].is_used

    def test_use_backup_code_twice_raises(self, email_user_auth: UserAuth, any_totp_secret: TwoFASecret) -> None:
        auth = email_user_auth
        auth.enable_auth_factor(TwoFactorMethod.TOTP, any_totp_secret)
        auth.generate_backup_codes(["hash1"])
        auth.use_backup_code("hash1", lambda plain, stored: plain == stored)
        with pytest.raises(InvalidBackupCodeException):
            auth.use_backup_code("hash1", lambda plain, stored: plain == stored)


# ═══════════════════════════════════════════════════════════════════════════
# OAuth
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestUserAuthOAuth:
    def test_link_oauth(self, email_user_auth: UserAuth) -> None:
        auth = email_user_auth
        auth.link_oauth(AuthProvider.OAUTH_GOOGLE, "google_123")
        assert len(auth.oauth_links) == 1

    def test_link_oauth_emits_event(self, email_user_auth: UserAuth) -> None:
        auth = email_user_auth
        auth.clear_domain_events()
        auth.link_oauth(AuthProvider.OAUTH_YANDEX, "yandex_456")
        events = auth.clear_domain_events()
        assert any(isinstance(e, OAuthLinked) for e in events)

    def test_link_already_linked_raises(self, oauth_user_auth: UserAuth) -> None:
        auth = oauth_user_auth
        with pytest.raises(OAuthProviderAlreadyLinkedException):
            auth.link_oauth(AuthProvider.OAUTH_GOOGLE, "another_id")

    def test_unlink_oauth(self, oauth_user_auth: UserAuth) -> None:
        auth = oauth_user_auth
        auth.password_hash = PasswordHash("some_hash")
        auth.unlink_oauth(AuthProvider.OAUTH_GOOGLE)
        assert len(auth.oauth_links) == 0

    def test_unlink_oauth_emits_event(self, oauth_user_auth: UserAuth) -> None:
        auth = oauth_user_auth
        auth.password_hash = PasswordHash("some_hash")
        auth.clear_domain_events()
        auth.unlink_oauth(AuthProvider.OAUTH_GOOGLE)
        events = auth.clear_domain_events()
        assert any(isinstance(e, OAuthUnlinked) for e in events)

    def test_unlink_last_provider_without_password_raises(self, oauth_user_auth: UserAuth) -> None:
        auth = oauth_user_auth
        with pytest.raises(CannotUnlinkLastProviderException):
            auth.unlink_oauth(AuthProvider.OAUTH_GOOGLE)


# ═══════════════════════════════════════════════════════════════════════════
# Доверенные устройства
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestUserAuthTrustedDevices:
    def test_add_trusted_device(self, email_user_auth: UserAuth, any_device_info: DeviceInfo, any_ip: IpAddress) -> None:
        auth = email_user_auth
        auth.add_trusted_device("fp_abc", any_device_info, any_ip)
        assert len(auth.trusted_devices) == 1

    def test_add_trusted_device_emits_event(self, email_user_auth: UserAuth, any_device_info: DeviceInfo, any_ip: IpAddress) -> None:
        auth = email_user_auth
        auth.clear_domain_events()
        auth.add_trusted_device("fp_abc", any_device_info, any_ip)
        events = auth.clear_domain_events()
        assert any(isinstance(e, TrustedDeviceAdded) for e in events)

    def test_add_duplicate_device_ignored(self, email_user_auth: UserAuth, any_device_info: DeviceInfo, any_ip: IpAddress) -> None:
        auth = email_user_auth
        auth.add_trusted_device("fp_abc", any_device_info, any_ip)
        auth.add_trusted_device("fp_abc", DeviceInfo(user_agent="Firefox"), IpAddress("10.0.0.1"))
        assert len(auth.trusted_devices) == 1


# ═══════════════════════════════════════════════════════════════════════════
# Пароль
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestUserAuthPassword:
    def test_change_password(self, email_user_auth: UserAuth) -> None:
        auth = email_user_auth
        new_hash = PasswordHash("$2b$12$new_hash")
        auth.change_password(new_hash)
        assert auth.password_hash == new_hash

    def test_change_password_emits_event(self, email_user_auth: UserAuth) -> None:
        auth = email_user_auth
        auth.clear_domain_events()
        auth.change_password(PasswordHash("$2b$12$new_hash"))
        events = auth.clear_domain_events()
        assert any(isinstance(e, PasswordChanged) for e in events)


# ═══════════════════════════════════════════════════════════════════════════
# Успешный вход
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestUserAuthSuccessfulLogin:
    def test_record_successful_login_resets_counter(self, email_user_auth: UserAuth, default_lockout_policy: FailedLoginPolicy) -> None:
        auth = email_user_auth
        for _ in range(2):
            auth.record_failed_login(default_lockout_policy)
        auth.record_successful_login()
        assert auth.failed_login_attempts == 0

    def test_record_successful_login_emits_event(self, email_user_auth: UserAuth) -> None:
        auth = email_user_auth
        auth.clear_domain_events()
        auth.record_successful_login(session_id="sess-1", ip=IpAddress("10.0.0.1"), device="Chrome")
        events = auth.clear_domain_events()
        assert any(isinstance(e, UserLoggedIn) for e in events)


# ═══════════════════════════════════════════════════════════════════════════
# Уведомление о новом устройстве
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestUserAuthNewDeviceNotification:
    def test_notify_new_device_login(self, email_user_auth: UserAuth) -> None:
        auth = email_user_auth
        auth.clear_domain_events()
        auth.notify_new_device_login(ip="10.0.0.1", device="Chrome/Windows")
        events = auth.clear_domain_events()
        assert any(isinstance(e, NewDeviceLogin) for e in events)
        event = next(e for e in events if isinstance(e, NewDeviceLogin))
        assert event.ip == "10.0.0.1"
        assert event.device == "Chrome/Windows"

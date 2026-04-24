from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from app.shared.domain.base_aggregate import AggregateRoot
from app.shared.domain.value_objects.email_vo import Email
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.ip_address_vo import IpAddress
from app.context.identity.domain.entities.auth_factor import AuthFactor
from app.context.identity.domain.entities.backup_code import BackupCode
from app.context.identity.domain.entities.email_verification import EmailVerification
from app.context.identity.domain.entities.login_attempt import LoginAttempt
from app.context.identity.domain.entities.oauth_link import OAuthLink
from app.context.identity.domain.entities.trusted_device import TrustedDevice
from app.context.identity.domain.events.auth_events import (
    AuthFactorDisabled,
    AuthFactorEnabled,
    LoginFailed,
    NewDeviceLogin,
    OAuthLinked,
    OAuthUnlinked,
    PasswordResetCompleted,
    PasswordResetRequested,
    SSOLinked,
    TrustedDeviceAdded,
    TrustedDeviceRemoved,
    UserLockedOut,
    UserLoggedIn,
)
from app.context.identity.domain.events.user_events import PasswordChanged
from app.context.identity.domain.exceptions.auth_exceptions import (
    OAuthProviderAlreadyLinkedException,
)
from app.context.identity.domain.exceptions.user_exceptions import (
    CannotUnlinkLastProviderException,
    InvalidBackupCodeException,
    InvalidVerificationTokenException,
    UserBlockedException,
)
from app.context.identity.domain.value_objects.auth_provider import AuthProvider
from app.context.identity.domain.value_objects.device_info import DeviceInfo
from app.context.identity.domain.value_objects.failed_login_policy import FailedLoginPolicy
from app.context.identity.domain.value_objects.login_status import LoginStatus
from app.context.identity.domain.value_objects.password_hash import PasswordHash
from app.context.identity.domain.value_objects.two_fa_secret import TwoFASecret
from app.context.identity.domain.value_objects.two_factor_method import TwoFactorMethod
from app.context.identity.domain.value_objects.verification_token import VerificationToken
from app.context.identity.domain.value_objects.verification_type import VerificationType


@dataclass
class UserAuth(AggregateRoot):
    """
    Корень агрегата аутентификации пользователя (Identity BC).

    Отвечает за аутентификацию: пароль, OAuth, 2FA, блокировки,
    верификации. Связан с User через user_id (opaque ID).

    Атрибуты:
        user_id: ID пользователя (opaque, ссылка на агрегат User).
        email: Email-адрес (для поиска по email).
        password_hash: Хеш пароля (None для OAuth/SSO-only).
        auth_factors: Коллекция факторов 2FA.
        oauth_links: Список привязок OAuth/SSO провайдеров.
        login_attempts: Записи попыток входа.
        trusted_devices: Список доверенных устройств.
        verifications: Список верификаций (email, сброс пароля и др.).
        backup_codes: Список резервных кодов 2FA.
        failed_login_attempts: Счётчик неудачных попыток входа.
        locked_until: Время автоматической разблокировки.
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    user_id: Id = field(default_factory=Id.generate)
    email: Email = field(default_factory=lambda: Email("user@example.com"))
    password_hash: PasswordHash | None = None
    auth_factors: list[AuthFactor] = field(default_factory=list)
    oauth_links: list[OAuthLink] = field(default_factory=list)
    login_attempts: list[LoginAttempt] = field(default_factory=list)
    trusted_devices: list[TrustedDevice] = field(default_factory=list)
    verifications: list[EmailVerification] = field(default_factory=list)
    backup_codes: list[BackupCode] = field(default_factory=list)
    failed_login_attempts: int = 0
    locked_until: datetime | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    # --- Фабричные методы ---

    @classmethod
    def create_for_email_auth(
        cls, user_id: Id, email: Email, password_hash: PasswordHash
    ) -> UserAuth:
        """Создаёт UserAuth для регистрации по email + пароль."""
        auth = cls(
            user_id=user_id,
            email=email,
            password_hash=password_hash,
        )
        return auth

    @classmethod
    def create_for_oauth(
        cls,
        user_id: Id,
        email: Email,
        provider: AuthProvider,
        provider_user_id: str,
    ) -> UserAuth:
        """Создаёт UserAuth для регистрации через OAuth."""
        oauth_link = OAuthLink(
            provider=provider,
            provider_user_id=provider_user_id,
            email=email.value,
        )
        auth = cls(
            user_id=user_id,
            email=email,
            password_hash=None,
            oauth_links=[oauth_link],
        )
        auth._register_event(
            OAuthLinked(user_id=str(user_id), provider=provider)
        )
        return auth

    @classmethod
    def create_for_sso(
        cls, user_id: Id, email: Email, provider_user_id: str
    ) -> UserAuth:
        """Создаёт UserAuth для регистрации через SSO."""
        oauth_link = OAuthLink(
            provider=AuthProvider.SAML_SSO,
            provider_user_id=provider_user_id,
            email=email.value,
        )
        auth = cls(
            user_id=user_id,
            email=email,
            password_hash=None,
            oauth_links=[oauth_link],
        )
        auth._register_event(
            SSOLinked(user_id=str(user_id))
        )
        return auth

    # --- Пароль ---

    def verify_password(self, password_hash: PasswordHash) -> bool:
        """Проверяет пароль (сравнение хешей выполняется на инфраструктурном уровне)."""
        return self.password_hash is not None and self.password_hash == password_hash

    def change_password(self, new_password_hash: PasswordHash) -> None:
        """Сменяет пароль."""
        self.password_hash = new_password_hash
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            PasswordChanged(user_id=str(self.user_id))
        )

    def request_password_reset(self, token: VerificationToken, expires_at: datetime) -> VerificationToken:
        """Запрашивает сброс пароля."""
        reset_token = VerificationToken(
            value=token.value,
            token_type=VerificationType.PASSWORD_RESET,
            expires_at=expires_at,
        )
        verification = EmailVerification(
            verification_type=VerificationType.PASSWORD_RESET,
            token=reset_token,
            expires_at=expires_at,
        )
        self.verifications.append(verification)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            PasswordResetRequested(user_id=str(self.user_id), email=self.email.value)
        )
        return reset_token

    def reset_password(self, token_value: str, new_password_hash: PasswordHash) -> None:
        """Сбрасывает пароль по токену."""
        verification = self._find_verification(token_value, VerificationType.PASSWORD_RESET)
        if verification is None or verification.is_used or verification.is_expired():
            raise InvalidVerificationTokenException()
        verification.mark_used()
        self.password_hash = new_password_hash
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            PasswordResetCompleted(user_id=str(self.user_id))
        )

    # --- Email верификация ---

    def request_email_verification(self, token: VerificationToken, expires_at: datetime) -> VerificationToken:
        """Запрашивает верификацию email."""
        verify_token = VerificationToken(
            value=token.value,
            token_type=VerificationType.EMAIL_CONFIRMATION,
            expires_at=expires_at,
        )
        verification = EmailVerification(
            verification_type=VerificationType.EMAIL_CONFIRMATION,
            token=verify_token,
            expires_at=expires_at,
        )
        self.verifications.append(verification)
        self.updated_at = datetime.now(tz=timezone.utc)
        return verify_token

    def verify_email(self, token_value: str) -> None:
        """Подтверждает email по токену."""
        verification = self._find_verification(token_value, VerificationType.EMAIL_CONFIRMATION)
        if verification is None or verification.is_used or verification.is_expired():
            raise InvalidVerificationTokenException()
        verification.mark_used()
        self.updated_at = datetime.now(tz=timezone.utc)

    # --- Блокировка / попытки входа ---

    def record_failed_login(
        self,
        policy: FailedLoginPolicy,
        ip: IpAddress | None = None,
        user_agent: str = "",
    ) -> None:
        """Фиксирует неудачную попытку входа. Блокирует по политике."""
        login_ip = ip if ip is not None else IpAddress("0.0.0.0")
        attempt = LoginAttempt(
            ip=login_ip,
            user_agent=user_agent,
            was_successful=False,
            login_status=LoginStatus.FAILED,
        )
        self.login_attempts.append(attempt)
        self.failed_login_attempts += 1
        threshold = policy.get_threshold_for_attempts(self.failed_login_attempts)
        if threshold is not None:
            self.locked_until = datetime.now(tz=timezone.utc) + timedelta(
                minutes=threshold.lock_duration_minutes
            )
            self._register_event(
                UserLockedOut(
                    user_id=str(self.user_id),
                    lockout_until=self.locked_until.isoformat(),
                )
            )
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            LoginFailed(user_id=str(self.user_id), ip=login_ip.value)
        )

    def record_successful_login(
        self,
        session_id: str = "",
        ip: IpAddress | None = None,
        device: str = "",
    ) -> None:
        """Сбрасывает счётчик неудачных попыток после успешного входа."""
        login_ip = ip if ip is not None else IpAddress("0.0.0.0")
        attempt = LoginAttempt(
            ip=login_ip,
            user_agent=device,
            was_successful=True,
            login_status=LoginStatus.SUCCESS,
        )
        self.login_attempts.append(attempt)
        self.failed_login_attempts = 0
        self.locked_until = None
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            UserLoggedIn(
                user_id=str(self.user_id),
                session_id=session_id,
                ip=login_ip.value,
                device=device,
            )
        )

    def unlock(self) -> None:
        """Разблокирует аккаунт."""
        self.failed_login_attempts = 0
        self.locked_until = None
        self.updated_at = datetime.now(tz=timezone.utc)

    def is_locked(self) -> bool:
        """Проверяет, заблокирован ли аккаунт."""
        if self.locked_until is None:
            return False
        if datetime.now(tz=timezone.utc) > self.locked_until:
            self.unlock()
            return False
        return True

    # --- 2FA ---

    def enable_auth_factor(
        self, method: TwoFactorMethod, secret: TwoFASecret, is_primary: bool = False
    ) -> None:
        """Включает фактор 2FA."""
        existing = self._find_auth_factor(method)
        if existing is not None and existing.is_enabled:
            return
        if existing is not None:
            existing.enable(secret, is_primary)
        else:
            factor = AuthFactor(
                method=method,
                secret=secret,
                is_enabled=True,
                is_primary=is_primary,
                priority=len(self.auth_factors),
            )
            self.auth_factors.append(factor)
        if is_primary:
            for f in self.auth_factors:
                if f.method != method:
                    f.is_primary = False
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            AuthFactorEnabled(
                user_id=str(self.user_id), method=method, is_primary=is_primary
            )
        )

    def disable_auth_factor(self, method: TwoFactorMethod) -> None:
        """Отключает фактор 2FA."""
        factor = self._find_auth_factor(method)
        if factor is None or not factor.is_enabled:
            return
        factor.disable()
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            AuthFactorDisabled(user_id=str(self.user_id), method=method)
        )

    def verify_auth_factor(self, method: TwoFactorMethod, code: str) -> bool:
        """Проверяет код 2FA (верификация выполняется на инфраструктурном уровне)."""
        factor = self._find_auth_factor(method)
        if factor is None or not factor.is_enabled:
            return False
        factor.verified_at = datetime.now(tz=timezone.utc)
        return True

    def set_primary_factor(self, method: TwoFactorMethod) -> None:
        """Устанавливает основной фактор 2FA."""
        factor = self._find_auth_factor(method)
        if factor is None or not factor.is_enabled:
            return
        for f in self.auth_factors:
            f.is_primary = f.method == method
        self.updated_at = datetime.now(tz=timezone.utc)

    # --- Резервные коды ---

    def generate_backup_codes(self, code_hashes: list[str]) -> None:
        """Заменяет все резервные коды новыми (передаются уже хешированные)."""
        has_enabled_2fa = any(f.is_enabled for f in self.auth_factors)
        if not has_enabled_2fa:
            return
        self.backup_codes = [BackupCode(code_hash=h) for h in code_hashes]
        self.updated_at = datetime.now(tz=timezone.utc)

    def use_backup_code(self, plain_code: str, verify_fn: object) -> None:
        """Использует резервный код. Проверяет через verify_fn(plain, hash)."""
        from collections.abc import Callable

        verify: Callable[[str, str], bool] = verify_fn  # type: ignore[assignment]
        for code in self.backup_codes:
            if not code.is_used and verify(plain_code, code.code_hash):
                code.mark_used()
                self.updated_at = datetime.now(tz=timezone.utc)
                return
        raise InvalidBackupCodeException()

    # --- OAuth ---

    def link_oauth(
        self,
        provider: AuthProvider,
        provider_user_id: str,
        email: str | None = None,
        display_name: str | None = None,
    ) -> None:
        """Привязывает OAuth-провайдер к аккаунту."""
        if any(link.provider == provider for link in self.oauth_links):
            raise OAuthProviderAlreadyLinkedException(provider.value)
        oauth_link = OAuthLink(
            provider=provider,
            provider_user_id=provider_user_id,
            email=email,
            display_name=display_name,
        )
        self.oauth_links.append(oauth_link)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            OAuthLinked(user_id=str(self.user_id), provider=provider)
        )

    def unlink_oauth(self, provider: AuthProvider) -> None:
        """Отвязывает OAuth-провайдер от аккаунта."""
        if not any(link.provider == provider for link in self.oauth_links):
            return
        has_password = self.password_hash is not None
        other_links = [link for link in self.oauth_links if link.provider != provider]
        if not has_password and len(other_links) == 0:
            raise CannotUnlinkLastProviderException()
        self.oauth_links = other_links
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            OAuthUnlinked(user_id=str(self.user_id), provider=provider)
        )

    # --- Доверенные устройства ---

    def add_trusted_device(
        self,
        fingerprint: str,
        device_info: DeviceInfo,
        ip: IpAddress,
        expires_at: datetime | None = None,
    ) -> None:
        """Добавляет доверенное устройство."""
        existing = self._find_trusted_device(fingerprint)
        if existing is not None:
            return
        device = TrustedDevice(
            device_fingerprint=fingerprint,
            device_info=device_info,
            ip=ip,
            expires_at=expires_at,
        )
        self.trusted_devices.append(device)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            TrustedDeviceAdded(
                user_id=str(self.user_id), device_fingerprint=fingerprint
            )
        )

    def remove_trusted_device(self, fingerprint: str) -> None:
        """Удаляет доверенное устройство."""
        self.trusted_devices = [
            d for d in self.trusted_devices if d.device_fingerprint != fingerprint
        ]
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            TrustedDeviceRemoved(
                user_id=str(self.user_id), device_fingerprint=fingerprint
            )
        )

    def is_trusted_device(self, fingerprint: str) -> bool:
        """Проверяет, является ли устройство доверенным."""
        device = self._find_trusted_device(fingerprint)
        return device is not None and not device.is_expired()

    def notify_new_device_login(self, ip: str, device: str) -> None:
        """Фиксирует вход с нового устройства/IP. Вызывается из app-layer."""
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            NewDeviceLogin(user_id=str(self.user_id), ip=ip, device=device)
        )

    # --- Приватные методы ---

    def _find_verification(self, token_value: str, verification_type: VerificationType) -> EmailVerification | None:
        """Ищет верификацию по токену и типу."""
        for v in reversed(self.verifications):
            if v.token.value == token_value and v.verification_type == verification_type:
                return v
        return None

    def _find_auth_factor(self, method: TwoFactorMethod) -> AuthFactor | None:
        """Ищет фактор 2FA по методу."""
        for f in self.auth_factors:
            if f.method == method:
                return f
        return None

    def _find_trusted_device(self, fingerprint: str) -> TrustedDevice | None:
        """Ищет доверенное устройство по отпечатку."""
        for d in self.trusted_devices:
            if d.device_fingerprint == fingerprint:
                return d
        return None

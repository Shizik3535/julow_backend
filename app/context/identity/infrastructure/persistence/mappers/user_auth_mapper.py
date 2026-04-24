from __future__ import annotations

from app.shared.domain.value_objects.email_vo import Email
from app.shared.domain.value_objects.ip_address_vo import IpAddress
from app.shared.infrastructure.persistence.sqlalchemy_base_mapper import BaseMapper
from app.context.identity.domain.aggregates.user_auth import UserAuth
from app.context.identity.domain.entities.auth_factor import AuthFactor
from app.context.identity.domain.entities.backup_code import BackupCode
from app.context.identity.domain.entities.email_verification import EmailVerification
from app.context.identity.domain.entities.login_attempt import LoginAttempt
from app.context.identity.domain.entities.oauth_link import OAuthLink
from app.context.identity.domain.entities.trusted_device import TrustedDevice
from app.context.identity.domain.value_objects.auth_provider import AuthProvider
from app.context.identity.domain.value_objects.device_info import DeviceInfo
from app.context.identity.domain.value_objects.login_status import LoginStatus
from app.context.identity.domain.value_objects.password_hash import PasswordHash
from app.context.identity.domain.value_objects.two_fa_secret import TwoFASecret
from app.context.identity.domain.value_objects.two_factor_method import TwoFactorMethod
from app.context.identity.domain.value_objects.verification_token import VerificationToken
from app.context.identity.domain.value_objects.verification_type import VerificationType
from app.context.identity.infrastructure.persistence.orm_models.user_auth_orm import (
    AuthFactorORM,
    BackupCodeORM,
    EmailVerificationORM,
    LoginAttemptORM,
    OAuthLinkORM,
    TrustedDeviceORM,
    UserAuthORM,
)


class UserAuthMapper(BaseMapper[UserAuth, UserAuthORM]):
    """Data Mapper: UserAuth ↔ UserAuthORM (включая все дочерние сущности)."""

    # --- Main aggregate ---

    def to_domain(self, orm_model: UserAuthORM) -> UserAuth:
        password_hash = None
        if orm_model.password_hash:
            password_hash = PasswordHash(value=orm_model.password_hash)

        return UserAuth(
            id=self._map_id(orm_model.id),
            user_id=self._map_id(orm_model.user_id),
            email=Email(orm_model.email),
            password_hash=password_hash,
            auth_factors=[self._factor_to_domain(f) for f in orm_model.auth_factors],
            oauth_links=[self._oauth_to_domain(o) for o in orm_model.oauth_links],
            login_attempts=[self._attempt_to_domain(a) for a in orm_model.login_attempts],
            trusted_devices=[self._device_to_domain(d) for d in orm_model.trusted_devices],
            verifications=[self._verification_to_domain(v) for v in orm_model.email_verifications],
            backup_codes=[self._backup_to_domain(b) for b in orm_model.backup_codes],
            failed_login_attempts=orm_model.failed_login_attempts,
            locked_until=orm_model.locked_until,
            created_at=orm_model.created_at,
            updated_at=orm_model.updated_at,
        )

    def to_orm(self, aggregate: UserAuth) -> UserAuthORM:
        orm = UserAuthORM(
            id=self._map_uuid(aggregate.id),
            user_id=self._map_uuid(aggregate.user_id),
            email=aggregate.email.value,
            password_hash=aggregate.password_hash.value if aggregate.password_hash else None,
            failed_login_attempts=aggregate.failed_login_attempts,
            locked_until=aggregate.locked_until,
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,
        )
        orm.auth_factors = [self._factor_to_orm(f, orm.id) for f in aggregate.auth_factors]
        orm.oauth_links = [self._oauth_to_orm(o, orm.id) for o in aggregate.oauth_links]
        orm.login_attempts = [self._attempt_to_orm(a, orm.id) for a in aggregate.login_attempts]
        orm.trusted_devices = [self._device_to_orm(d, orm.id) for d in aggregate.trusted_devices]
        orm.email_verifications = [self._verification_to_orm(v, orm.id) for v in aggregate.verifications]
        orm.backup_codes = [self._backup_to_orm(b, orm.id) for b in aggregate.backup_codes]
        return orm

    # --- AuthFactor ---

    def _factor_to_domain(self, orm: AuthFactorORM) -> AuthFactor:
        secret = None
        if orm.secret_value:
            secret = TwoFASecret(
                value=orm.secret_value,
                method=TwoFactorMethod(orm.secret_method) if orm.secret_method else TwoFactorMethod.TOTP,
            )
        return AuthFactor(
            id=self._map_id(orm.id),
            method=TwoFactorMethod(orm.method),
            secret=secret,
            is_enabled=orm.is_enabled,
            is_primary=orm.is_primary,
            verified_at=orm.verified_at,
            priority=orm.priority,
        )

    def _factor_to_orm(self, entity: AuthFactor, parent_id) -> AuthFactorORM:
        return AuthFactorORM(
            id=self._map_uuid(entity.id),
            user_auth_id=parent_id,
            method=entity.method.value,
            secret_value=entity.secret.value if entity.secret else None,
            secret_method=entity.secret.method.value if entity.secret else None,
            is_enabled=entity.is_enabled,
            is_primary=entity.is_primary,
            verified_at=entity.verified_at,
            priority=entity.priority,
        )

    # --- OAuthLink ---

    def _oauth_to_domain(self, orm: OAuthLinkORM) -> OAuthLink:
        return OAuthLink(
            id=self._map_id(orm.id),
            provider=AuthProvider(orm.provider),
            provider_user_id=orm.provider_user_id,
            email=orm.email,
            display_name=orm.display_name,
            linked_at=orm.linked_at,
        )

    def _oauth_to_orm(self, entity: OAuthLink, parent_id) -> OAuthLinkORM:
        return OAuthLinkORM(
            id=self._map_uuid(entity.id),
            user_auth_id=parent_id,
            provider=entity.provider.value,
            provider_user_id=entity.provider_user_id,
            email=entity.email,
            display_name=entity.display_name,
            linked_at=entity.linked_at,
        )

    # --- LoginAttempt ---

    def _attempt_to_domain(self, orm: LoginAttemptORM) -> LoginAttempt:
        return LoginAttempt(
            id=self._map_id(orm.id),
            ip=IpAddress(orm.ip),
            user_agent=orm.user_agent,
            attempted_at=orm.attempted_at,
            was_successful=orm.was_successful,
            login_status=LoginStatus(orm.login_status),
        )

    def _attempt_to_orm(self, entity: LoginAttempt, parent_id) -> LoginAttemptORM:
        return LoginAttemptORM(
            id=self._map_uuid(entity.id),
            user_auth_id=parent_id,
            ip=entity.ip.value,
            user_agent=entity.user_agent,
            attempted_at=entity.attempted_at,
            was_successful=entity.was_successful,
            login_status=entity.login_status.value,
        )

    # --- TrustedDevice ---

    def _device_to_domain(self, orm: TrustedDeviceORM) -> TrustedDevice:
        return TrustedDevice(
            id=self._map_id(orm.id),
            device_fingerprint=orm.device_fingerprint,
            device_info=DeviceInfo(
                user_agent=orm.user_agent,
                os=orm.os,
                browser=orm.browser,
                device_type=orm.device_type,
            ),
            ip=IpAddress(orm.ip),
            trusted_at=orm.trusted_at,
            expires_at=orm.expires_at,
        )

    def _device_to_orm(self, entity: TrustedDevice, parent_id) -> TrustedDeviceORM:
        return TrustedDeviceORM(
            id=self._map_uuid(entity.id),
            user_auth_id=parent_id,
            device_fingerprint=entity.device_fingerprint,
            user_agent=entity.device_info.user_agent,
            os=entity.device_info.os,
            browser=entity.device_info.browser,
            device_type=entity.device_info.device_type,
            ip=entity.ip.value,
            trusted_at=entity.trusted_at,
            expires_at=entity.expires_at,
        )

    # --- EmailVerification ---

    def _verification_to_domain(self, orm: EmailVerificationORM) -> EmailVerification:
        return EmailVerification(
            id=self._map_id(orm.id),
            verification_type=VerificationType(orm.verification_type),
            token=VerificationToken(
                value=orm.token_value,
                token_type=VerificationType(orm.token_type),
                expires_at=orm.token_expires_at,
            ),
            is_used=orm.is_used,
            used_at=orm.used_at,
            expires_at=orm.expires_at,
        )

    def _verification_to_orm(self, entity: EmailVerification, parent_id) -> EmailVerificationORM:
        return EmailVerificationORM(
            id=self._map_uuid(entity.id),
            user_auth_id=parent_id,
            verification_type=entity.verification_type.value,
            token_value=entity.token.value,
            token_type=entity.token.token_type.value,
            token_expires_at=entity.token.expires_at,
            is_used=entity.is_used,
            used_at=entity.used_at,
            expires_at=entity.expires_at,
        )

    # --- BackupCode ---

    def _backup_to_domain(self, orm: BackupCodeORM) -> BackupCode:
        return BackupCode(
            id=self._map_id(orm.id),
            code_hash=orm.code_hash,
            is_used=orm.is_used,
            used_at=orm.used_at,
            created_at=orm.created_at,
        )

    def _backup_to_orm(self, entity: BackupCode, parent_id) -> BackupCodeORM:
        return BackupCodeORM(
            id=self._map_uuid(entity.id),
            user_auth_id=parent_id,
            code_hash=entity.code_hash,
            is_used=entity.is_used,
            used_at=entity.used_at,
        )

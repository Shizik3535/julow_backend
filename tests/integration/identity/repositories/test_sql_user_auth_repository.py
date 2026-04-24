"""Интеграционные тесты SqlUserAuthRepository (реальная PostgreSQL)."""

import uuid
from datetime import datetime, timedelta, timezone

import pytest

from app.shared.domain.value_objects.email_vo import Email
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.ip_address_vo import IpAddress
from app.context.identity.domain.aggregates.user_auth import UserAuth
from app.context.identity.domain.value_objects.auth_provider import AuthProvider
from app.context.identity.domain.value_objects.device_info import DeviceInfo
from app.context.identity.domain.value_objects.failed_login_policy import FailedLoginPolicy
from app.context.identity.domain.value_objects.lockout_threshold import LockoutThreshold
from app.context.identity.domain.value_objects.password_hash import PasswordHash
from app.context.identity.domain.value_objects.two_fa_secret import TwoFASecret
from app.context.identity.domain.value_objects.two_factor_method import TwoFactorMethod
from app.context.identity.domain.value_objects.verification_token import VerificationToken
from app.context.identity.domain.value_objects.verification_type import VerificationType
from app.context.identity.infrastructure.persistence.repositories.sql_user_auth_repository import (
    SqlUserAuthRepository,
)


@pytest.mark.integration
class TestSqlUserAuthRepositoryBasic:
    """Базовые CRUD тесты."""

    async def test_add_and_get_by_id(self, user_auth_repo: SqlUserAuthRepository, make_user_auth) -> None:
        auth = await make_user_auth()
        found = await user_auth_repo.get_by_id(auth.id)
        assert found is not None
        assert found.user_id == auth.user_id

    async def test_get_by_user_id(self, user_auth_repo: SqlUserAuthRepository, make_user_auth) -> None:
        auth = await make_user_auth()
        found = await user_auth_repo.get_by_user_id(auth.user_id)
        assert found is not None
        assert found.id == auth.id

    async def test_get_by_email(self, user_auth_repo: SqlUserAuthRepository, make_user_auth) -> None:
        email = f"auth-email-{uuid.uuid4().hex[:6]}@test.com"
        auth = await make_user_auth(email=email)
        found = await user_auth_repo.get_by_email(Email(email))
        assert found is not None
        assert found.id == auth.id

    async def test_get_by_email_not_found(self, user_auth_repo: SqlUserAuthRepository) -> None:
        found = await user_auth_repo.get_by_email(Email("none@test.com"))
        assert found is None


@pytest.mark.integration
class TestSqlUserAuthRepositoryOAuth:
    """Тесты OAuth-связей."""

    async def test_add_oauth_user_auth(self, user_auth_repo: SqlUserAuthRepository, make_user) -> None:
        user = await make_user()
        user_id = user.id
        email = Email(f"oauth-{uuid.uuid4().hex[:6]}@test.com")
        auth = UserAuth.create_for_oauth(
            user_id=user_id,
            email=email,
            provider=AuthProvider.OAUTH_GOOGLE,
            provider_user_id="google-id-123",
        )
        auth.clear_domain_events()
        await user_auth_repo.add(auth)

        found = await user_auth_repo.get_by_id(auth.id)
        assert found is not None
        assert len(found.oauth_links) == 1
        assert found.oauth_links[0].provider == AuthProvider.OAUTH_GOOGLE

    async def test_get_by_oauth_provider(self, user_auth_repo: SqlUserAuthRepository, make_user) -> None:
        user = await make_user()
        user_id = user.id
        email = Email(f"oauth-find-{uuid.uuid4().hex[:6]}@test.com")
        auth = UserAuth.create_for_oauth(
            user_id=user_id,
            email=email,
            provider=AuthProvider.OAUTH_GITHUB,
            provider_user_id="github-id-456",
        )
        auth.clear_domain_events()
        await user_auth_repo.add(auth)

        found = await user_auth_repo.get_by_oauth_provider(
            AuthProvider.OAUTH_GITHUB, "github-id-456"
        )
        assert found is not None
        assert found.id == auth.id


@pytest.mark.integration
class TestSqlUserAuthRepositoryUpdate:
    """Тесты обновления с дочерними коллекциями."""

    async def test_update_password(self, user_auth_repo: SqlUserAuthRepository, make_user_auth) -> None:
        auth = await make_user_auth()
        auth.change_password(PasswordHash(value="new-hash-value"))
        auth.clear_domain_events()
        await user_auth_repo.update(auth)

        found = await user_auth_repo.get_by_id(auth.id)
        assert found is not None
        assert found.password_hash is not None
        assert found.password_hash.value == "new-hash-value"

    async def test_update_with_login_attempts(self, user_auth_repo: SqlUserAuthRepository, make_user_auth) -> None:
        auth = await make_user_auth()
        policy = FailedLoginPolicy(thresholds=[
            LockoutThreshold(failed_attempts=5, lock_duration_minutes=15),
        ])
        auth.record_failed_login(policy, ip=IpAddress("1.2.3.4"), user_agent="TestAgent")
        auth.clear_domain_events()
        await user_auth_repo.update(auth)

        found = await user_auth_repo.get_by_id(auth.id)
        assert found is not None
        assert found.failed_login_attempts == 1
        assert len(found.login_attempts) == 1

    async def test_update_with_auth_factor(self, user_auth_repo: SqlUserAuthRepository, make_user_auth) -> None:
        auth = await make_user_auth()
        secret = TwoFASecret(value="JBSWY3DPEHPK3PXP", method=TwoFactorMethod.TOTP)
        auth.enable_auth_factor(method=TwoFactorMethod.TOTP, secret=secret, is_primary=True)
        auth.clear_domain_events()
        await user_auth_repo.update(auth)

        found = await user_auth_repo.get_by_id(auth.id)
        assert found is not None
        assert len(found.auth_factors) == 1
        assert found.auth_factors[0].method == TwoFactorMethod.TOTP
        assert found.auth_factors[0].is_primary is True

    async def test_update_with_email_verification(
        self, user_auth_repo: SqlUserAuthRepository, make_user_auth
    ) -> None:
        auth = await make_user_auth()
        expires_at = datetime.now(tz=timezone.utc) + timedelta(hours=24)
        token = VerificationToken(
            value="verify-token-123",
            token_type=VerificationType.EMAIL_CONFIRMATION,
            expires_at=expires_at,
        )
        auth.request_email_verification(token=token, expires_at=expires_at)
        await user_auth_repo.update(auth)

        found = await user_auth_repo.get_by_id(auth.id)
        assert found is not None
        assert len(found.verifications) == 1

    async def test_update_with_trusted_device(self, user_auth_repo: SqlUserAuthRepository, make_user_auth) -> None:
        auth = await make_user_auth()
        auth.add_trusted_device(
            fingerprint="device-fp-123",
            device_info=DeviceInfo(user_agent="TrustedBrowser"),
            ip=IpAddress("10.0.0.5"),
        )
        auth.clear_domain_events()
        await user_auth_repo.update(auth)

        found = await user_auth_repo.get_by_id(auth.id)
        assert found is not None
        assert len(found.trusted_devices) == 1
        assert found.trusted_devices[0].device_fingerprint == "device-fp-123"

    async def test_update_with_backup_codes(self, user_auth_repo: SqlUserAuthRepository, make_user_auth) -> None:
        auth = await make_user_auth()
        # Сначала включаем 2FA (требуется для backup codes)
        secret = TwoFASecret(value="JBSWY3DPEHPK3PXP", method=TwoFactorMethod.TOTP)
        auth.enable_auth_factor(method=TwoFactorMethod.TOTP, secret=secret)
        auth.generate_backup_codes(["hash1", "hash2", "hash3"])
        auth.clear_domain_events()
        await user_auth_repo.update(auth)

        found = await user_auth_repo.get_by_id(auth.id)
        assert found is not None
        assert len(found.backup_codes) == 3

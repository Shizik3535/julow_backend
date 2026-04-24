"""Unit-тесты для EmailVerification."""

from datetime import datetime, timedelta, timezone

import pytest

from app.context.identity.domain.entities.email_verification import EmailVerification
from app.context.identity.domain.value_objects.verification_token import VerificationToken
from app.context.identity.domain.value_objects.verification_type import VerificationType


@pytest.mark.unit
class TestEmailVerification:
    def test_create_email_confirmation(self) -> None:
        token = VerificationToken(value="a" * 32)
        expires = datetime.now(tz=timezone.utc) + timedelta(hours=1)
        ev = EmailVerification(
            verification_type=VerificationType.EMAIL_CONFIRMATION,
            token=token,
            expires_at=expires,
        )
        assert ev.verification_type == VerificationType.EMAIL_CONFIRMATION
        assert ev.token == token
        assert not ev.is_used
        assert not ev.is_expired()

    def test_create_password_reset(self) -> None:
        token = VerificationToken(value="b" * 32)
        expires = datetime.now(tz=timezone.utc) + timedelta(hours=1)
        ev = EmailVerification(
            verification_type=VerificationType.PASSWORD_RESET,
            token=token,
            expires_at=expires,
        )
        assert ev.verification_type == VerificationType.PASSWORD_RESET

    def test_is_expired_when_past(self) -> None:
        token = VerificationToken(value="c" * 32)
        expires = datetime.now(tz=timezone.utc) - timedelta(hours=1)
        ev = EmailVerification(token=token, expires_at=expires)
        assert ev.is_expired()

    def test_is_not_expired_when_future(self) -> None:
        token = VerificationToken(value="d" * 32)
        expires = datetime.now(tz=timezone.utc) + timedelta(hours=1)
        ev = EmailVerification(token=token, expires_at=expires)
        assert not ev.is_expired()

    def test_mark_used(self) -> None:
        token = VerificationToken(value="e" * 32)
        expires = datetime.now(tz=timezone.utc) + timedelta(hours=1)
        ev = EmailVerification(token=token, expires_at=expires)
        ev.mark_used()
        assert ev.is_used
        assert ev.used_at is not None

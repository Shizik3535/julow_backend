from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_value_object import ValueObject
from app.shared.domain.exceptions import ValidationException
from app.context.identity.domain.value_objects.verification_type import VerificationType


@dataclass(frozen=True)
class VerificationToken(ValueObject):
    """
    Value Object для токена верификации (подтверждение email, сброс пароля и др.).

    Атрибуты:
        value: Криптографически стойкий токен.
        token_type: Тип верификации.
        expires_at: Время истечения токена.
    """

    value: str
    token_type: VerificationType = VerificationType.EMAIL_CONFIRMATION
    expires_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    def __post_init__(self) -> None:
        if not self.value or len(self.value.strip()) < 16:
            raise ValidationException(
                field="verification_token",
                message="Токен верификации должен содержать минимум 16 символов",
            )

    def is_expired(self) -> bool:
        """Проверяет, истёк ли срок действия токена."""
        return datetime.now(tz=timezone.utc) > self.expires_at

    def __str__(self) -> str:
        return self.value

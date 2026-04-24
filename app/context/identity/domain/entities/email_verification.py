from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_entity import BaseEntity
from app.context.identity.domain.value_objects.verification_token import VerificationToken
from app.context.identity.domain.value_objects.verification_type import VerificationType


@dataclass
class EmailVerification(BaseEntity):
    """
    Сущность верификации email (подтверждение / сброс пароля).

    Принадлежит агрегату User. Хранит токен верификации
    и отслеживает его использование и срок действия.

    Атрибуты:
        id: Уникальный идентификатор записи.
        verification_type: Тип верификации (подтверждение email / сброс пароля).
        token: Токен верификации.
        is_used: Был ли токен использован.
        used_at: Время использования токена.
        expires_at: Время истечения токена.
        created_at: Время создания токена.
    """

    verification_type: VerificationType = VerificationType.EMAIL_CONFIRMATION
    token: VerificationToken = field(default_factory=lambda: VerificationToken(value="x" * 32))
    is_used: bool = False
    used_at: datetime | None = None
    expires_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    def is_expired(self) -> bool:
        """Проверяет, истёк ли срок действия токена."""
        return datetime.now(tz=timezone.utc) > self.expires_at

    def mark_used(self) -> None:
        """Помечает токен как использованный."""
        self.is_used = True
        self.used_at = datetime.now(tz=timezone.utc)

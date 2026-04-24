from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.shared.domain.base_value_object import ValueObject
from app.shared.domain.exceptions import ValidationException


@dataclass(frozen=True)
class InvitationToken(ValueObject):
    """
    Value Object для токена ссылки-приглашения.

    Атрибуты:
        value: Уникальное значение токена.
        expires_at: Время истечения (None — без ограничения).
        max_uses: Максимальное количество использований (None — без ограничения).
        used_count: Количество использований.
    """

    value: str
    expires_at: datetime | None = None
    max_uses: int | None = None
    used_count: int = 0

    def __post_init__(self) -> None:
        if not self.value:
            raise ValidationException(
                field="invitation_token",
                message="Значение токена не может быть пустым",
            )
        if self.max_uses is not None and self.max_uses < 1:
            raise ValidationException(
                field="invitation_token",
                message="Максимальное количество использований должно быть не менее 1",
            )
        if self.used_count < 0:
            raise ValidationException(
                field="invitation_token",
                message="Количество использований не может быть отрицательным",
            )

    @property
    def is_expired(self) -> bool:
        """Проверяет, истёк ли токен."""
        if self.expires_at is None:
            return False
        return datetime.now(tz=self.expires_at.tzinfo) > self.expires_at

    @property
    def is_max_uses_exceeded(self) -> bool:
        """Проверяет, исчерпан ли лимит использований."""
        if self.max_uses is None:
            return False
        return self.used_count >= self.max_uses

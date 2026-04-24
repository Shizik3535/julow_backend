from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_entity import BaseEntity
from app.context.identity.domain.value_objects.two_factor_method import TwoFactorMethod
from app.context.identity.domain.value_objects.two_fa_secret import TwoFASecret


@dataclass
class AuthFactor(BaseEntity):
    """
    Сущность фактора аутентификации (2FA).

    Принадлежит агрегату UserAuth как элемент коллекции.
    Каждый фактор — отдельная запись, что позволяет:
    несколько методов 2FA одновременно, резервные методы (fallback),
    приоритеты, добавление новых методов без изменения структуры.

    Атрибуты:
        id: Уникальный идентификатор записи.
        method: Метод 2FA (TOTP, EMAIL_CODE, APP).
        secret: Секрет 2FA (зашифрованный).
        is_enabled: Включён ли фактор.
        is_primary: Является ли основным фактором.
        verified_at: Время верификации фактора.
        priority: Приоритет фактора (0 — наивысший).
    """

    method: TwoFactorMethod = TwoFactorMethod.TOTP
    secret: TwoFASecret | None = None
    is_enabled: bool = False
    is_primary: bool = False
    verified_at: datetime | None = None
    priority: int = 0

    def enable(self, secret: TwoFASecret, is_primary: bool = False) -> None:
        """Включает фактор аутентификации."""
        self.secret = secret
        self.is_enabled = True
        self.is_primary = is_primary
        self.verified_at = datetime.now(tz=timezone.utc)

    def disable(self) -> None:
        """Отключает фактор аутентификации."""
        self.is_enabled = False
        self.is_primary = False

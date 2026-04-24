from __future__ import annotations

from datetime import datetime

from app.shared.application.base_dto import BaseDTO


class AuthFactorDTO(BaseDTO):
    """
    DTO фактора 2FA (Identity BC).

    Атрибуты:
        method: Метод 2FA (totp, email_code, app).
        is_enabled: Включён ли фактор.
        is_primary: Является ли основным.
        verified_at: Время последней верификации.
        priority: Приоритет фактора.
    """

    method: str
    is_enabled: bool
    is_primary: bool
    verified_at: datetime | None = None
    priority: int = 0

from __future__ import annotations

from enum import Enum


class TwoFactorMethod(Enum):
    """
    Метод двухфакторной аутентификации.

    Значения:
        TOTP: Time-based One-Time Password (приложение-аутентификатор).
        EMAIL_CODE: Код подтверждения на email.
        APP: Приложение-аутентификатор / резервные коды.
    """

    TOTP = "totp"
    EMAIL_CODE = "email_code"
    APP = "app"

from __future__ import annotations

from enum import Enum


class VerificationType(Enum):
    """
    Тип верификации.

    Значения:
        EMAIL_CONFIRMATION: Подтверждение email-адреса.
        PASSWORD_RESET: Сброс пароля.
        ACCOUNT_DELETION: Подтверждение удаления аккаунта.
        EMAIL_CHANGE: Подтверждение смены email.
    """

    EMAIL_CONFIRMATION = "email_confirmation"
    PASSWORD_RESET = "password_reset"
    ACCOUNT_DELETION = "account_deletion"
    EMAIL_CHANGE = "email_change"

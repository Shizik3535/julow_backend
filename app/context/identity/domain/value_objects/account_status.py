from __future__ import annotations

from enum import Enum


class AccountStatus(Enum):
    """
    Статус аккаунта пользователя.

    Значения:
        PENDING_VERIFICATION: Ожидает подтверждения email.
        ACTIVE: Аккаунт активен — полный доступ.
        LOCKED: Аккаунт заблокирован — вход невозможен (после N неудачных попыток).
        DISABLED: Аккаунт деактивирован — вход невозможен.
        PENDING_DELETION: Аккаунт в процессе удаления.
    """

    PENDING_VERIFICATION = "pending_verification"
    ACTIVE = "active"
    LOCKED = "locked"
    DISABLED = "disabled"
    PENDING_DELETION = "pending_deletion"

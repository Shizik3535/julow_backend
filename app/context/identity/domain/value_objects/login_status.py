from __future__ import annotations

from enum import Enum


class LoginStatus(Enum):
    """
    Статус попытки входа.

    Значения:
        SUCCESS: Успешный вход.
        FAILED: Неудачная попытка входа.
        BLOCKED: Вход заблокирован (аккаунт заблокирован).
    """

    SUCCESS = "success"
    FAILED = "failed"
    BLOCKED = "blocked"

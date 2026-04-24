from __future__ import annotations

from enum import Enum


class SessionStatus(Enum):
    """
    Статус сессии.

    Значения:
        ACTIVE: Сессия активна.
        EXPIRED: Срок действия сессии истёк.
        TERMINATED: Сессия завершена пользователем или системой.
    """

    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"

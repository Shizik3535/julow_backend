from __future__ import annotations

from enum import Enum


class RSVPStatus(Enum):
    """
    Статус ответа на приглашение.

    Значения:
        PENDING: Не ответил
        ACCEPTED: Примет участие
        DECLINED: Отклонил
        TENTATIVE: Под вопросом
    """

    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    TENTATIVE = "tentative"

from __future__ import annotations

from enum import Enum


class InvitationStatus(Enum):
    """
    Статус приглашения в проект.

    Значения:
        PENDING: Ожидает ответа
        ACCEPTED: Принято
        DECLINED: Отклонено
        EXPIRED: Истекло
        REVOKED: Отозвано
    """

    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    EXPIRED = "expired"
    REVOKED = "revoked"

from __future__ import annotations

from enum import Enum


class DigestFrequency(Enum):
    """
    Частота дайджеста уведомлений.

    Значения:
        DAILY: Ежедневный
        WEEKLY: Еженедельный
    """

    DAILY = "daily"
    WEEKLY = "weekly"

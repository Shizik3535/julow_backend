from __future__ import annotations

from enum import Enum


class ActivityTrackingConsent(Enum):
    """
    Согласие на отслеживание активности.

    Значения:
        GRANTED: Пользователь согласен.
        DENIED: Пользователь отказал.
    """

    GRANTED = "granted"
    DENIED = "denied"

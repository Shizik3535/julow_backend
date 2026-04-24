from __future__ import annotations

from enum import Enum


class RetroItemType(Enum):
    """
    Тип элемента ретроспективы.

    Значения:
        POSITIVE: Позитивный
        NEGATIVE: Негативный
        NEUTRAL: Нейтральный
        ACTION_ITEM: Пункт действий
    """

    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    ACTION_ITEM = "action_item"

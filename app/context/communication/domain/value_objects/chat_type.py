from __future__ import annotations

from enum import Enum


class ChatType(Enum):
    """
    Тип чата.

    Новые типы бесед = значение enum.

    Значения:
        DM: Личный диалог (2 участника)
        GROUP: Групповой чат
        CHANNEL: Публичный канал
        ANNOUNCEMENT: Канал объявлений
    """

    DM = "dm"
    GROUP = "group"
    CHANNEL = "channel"
    ANNOUNCEMENT = "announcement"

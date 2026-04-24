from __future__ import annotations

from enum import Enum


class MessageType(Enum):
    """
    Тип сообщения.

    Новые типы = значение enum.

    Значения:
        TEXT: Текстовое сообщение
        SYSTEM: Системное сообщение
        FILE: Файловое вложение
        IMAGE: Изображение
        VOICE: Голосовое сообщение
        VIDEO: Видео
    """

    TEXT = "text"
    SYSTEM = "system"
    FILE = "file"
    IMAGE = "image"
    VOICE = "voice"
    VIDEO = "video"

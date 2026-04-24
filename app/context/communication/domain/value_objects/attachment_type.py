from __future__ import annotations

from enum import Enum


class AttachmentType(Enum):
    """
    Тип вложения.

    Значения:
        IMAGE: Изображение
        VIDEO: Видео
        FILE: Файл
        LINK: Ссылка
        VOICE: Голосовое сообщение
    """

    IMAGE = "image"
    VIDEO = "video"
    FILE = "file"
    LINK = "link"
    VOICE = "voice"

from __future__ import annotations

from enum import Enum


class VirusScanStatus(Enum):
    """
    Статус сканирования на вирусы.

    Значения:
        PENDING: Ожидает сканирования
        CLEAN: Чистый
        INFECTED: Заражён
        SKIPPED: Пропущено
        ERROR: Ошибка сканирования
    """

    PENDING = "pending"
    CLEAN = "clean"
    INFECTED = "infected"
    SKIPPED = "skipped"
    ERROR = "error"

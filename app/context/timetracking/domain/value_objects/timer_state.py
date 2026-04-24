from __future__ import annotations

from enum import Enum


class TimerState(Enum):
    """
    Состояние таймера.

    Значения:
        RUNNING: Запущен
        PAUSED: На паузе
        STOPPED: Остановлен
    """

    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"

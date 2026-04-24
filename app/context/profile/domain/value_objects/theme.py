from __future__ import annotations

from enum import Enum


class Theme(Enum):
    """
    Тема оформления интерфейса.

    Значения:
        LIGHT: Светлая тема.
        DARK: Тёмная тема.
        SYSTEM: Следовать настройкам системы.
        CUSTOM: Пользовательская тема (активирует CustomTheme).
    """

    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"
    CUSTOM = "custom"

from __future__ import annotations

from enum import Enum


class InterfaceDensity(Enum):
    """
    Плотность интерфейса.

    Значения:
        COMPACT: Компактный — больше информации на экране.
        COMFORTABLE: Комфортный — баланс информативности и пространства.
        SPACIOUS: Просторный — максимум свободного места.
    """

    COMPACT = "compact"
    COMFORTABLE = "comfortable"
    SPACIOUS = "spacious"

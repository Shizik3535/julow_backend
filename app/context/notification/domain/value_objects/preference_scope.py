from __future__ import annotations

from enum import Enum


class PreferenceScope(Enum):
    """
    Область действия настройки уведомлений.

    Значения:
        GLOBAL: Глобальная настройка
        PROJECT: Настройка на уровне проекта
        WORKSPACE: Настройка на уровне workspace
    """

    GLOBAL = "global"
    PROJECT = "project"
    WORKSPACE = "workspace"

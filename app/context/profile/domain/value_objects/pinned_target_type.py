from __future__ import annotations

from enum import Enum


class PinnedTargetType(Enum):
    """
    Тип закреплённого элемента.

    Привязан к BC-моделям, стабилен. Добавление нового BC → новое значение.

    Значения:
        WORKSPACE: Workspace.
        PROJECT: Проект.
        TASK: Задача.
        DASHBOARD: Дашборд.
        REPORT: Отчёт.
    """

    WORKSPACE = "workspace"
    PROJECT = "project"
    TASK = "task"
    DASHBOARD = "dashboard"
    REPORT = "report"

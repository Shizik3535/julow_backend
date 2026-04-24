from __future__ import annotations

from enum import Enum


class HotkeyAction(Enum):
    """
    Действие горячей клавиши.

    Типобезопасная замена магических строк.
    Новые действия добавляются по мере развития UI.

    Значения:
        CREATE_TASK: Создать задачу.
        NAVIGATE_INBOX: Перейти во входящие.
        SEARCH: Поиск.
        TOGGLE_SIDEBAR: Показать/скрыть сайдбар.
        GO_HOME: Перейти на главную.
        QUICK_ACTION: Быстрое действие.
    """

    CREATE_TASK = "create_task"
    NAVIGATE_INBOX = "navigate_inbox"
    SEARCH = "search"
    TOGGLE_SIDEBAR = "toggle_sidebar"
    GO_HOME = "go_home"
    QUICK_ACTION = "quick_action"

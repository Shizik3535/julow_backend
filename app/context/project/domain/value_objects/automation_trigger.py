from __future__ import annotations

from enum import Enum


class AutomationTrigger(Enum):
    """
    Триггер автоматизации.

    Значения:
        STATUS_CHANGED: Статус изменён
        ASSIGNEE_CHANGED: Исполнитель изменён
        DUE_DATE_APPROACHING: Срок приближается
        PRIORITY_CHANGED: Приоритет изменён
        LABEL_ADDED: Метка добавлена
        COMMENT_ADDED: Комментарий добавлен
    """

    STATUS_CHANGED = "status_changed"
    ASSIGNEE_CHANGED = "assignee_changed"
    DUE_DATE_APPROACHING = "due_date_approaching"
    PRIORITY_CHANGED = "priority_changed"
    LABEL_ADDED = "label_added"
    COMMENT_ADDED = "comment_added"

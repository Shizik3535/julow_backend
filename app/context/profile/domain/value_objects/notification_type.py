from __future__ import annotations

from enum import Enum


class NotificationType(Enum):
    """
    Тип уведомления.

    Будет расти по мере добавления новых типов событий в системе.
    Новое значение = правка enum + миграция.

    Значения:
        TASK_ASSIGNED: Задача назначена.
        TASK_UPDATED: Задача обновлена.
        MENTION: Упоминание.
        COMMENT_ADDED: Комментарий добавлен.
        MEETING_REMINDER: Напоминание о встрече.
        SYSTEM_ANNOUNCEMENT: Системное объявление.
        DEADLINE_APPROACHING: Приближается дедлайн.
    """

    TASK_ASSIGNED = "task_assigned"
    TASK_UPDATED = "task_updated"
    MENTION = "mention"
    COMMENT_ADDED = "comment_added"
    MEETING_REMINDER = "meeting_reminder"
    SYSTEM_ANNOUNCEMENT = "system_announcement"
    DEADLINE_APPROACHING = "deadline_approaching"

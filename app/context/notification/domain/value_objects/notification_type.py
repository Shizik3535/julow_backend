from __future__ import annotations

from enum import Enum


class NotificationType(Enum):
    """
    Тип уведомления.

    Новые типы = значение enum.

    Значения:
        TASK_ASSIGNED: Задача назначена
        MENTIONED: Пользователь упомянут
        STATUS_CHANGED: Статус изменён
        DEADLINE_APPROACHING: Дедлайн приближается
        OVERDUE_TASK: Задача просрочена
        NEW_COMMENT: Новый комментарий
        WATCHER_UPDATED: Обновление наблюдателя
        INVITED: Приглашение
        SPRINT_COMPLETED: Спринт завершён
        SYSTEM: Системное уведомление
        BILLING: Биллинг
        SECURITY: Безопасность
    """

    TASK_ASSIGNED = "task_assigned"
    MENTIONED = "mentioned"
    STATUS_CHANGED = "status_changed"
    DEADLINE_APPROACHING = "deadline_approaching"
    OVERDUE_TASK = "overdue_task"
    NEW_COMMENT = "new_comment"
    WATCHER_UPDATED = "watcher_updated"
    INVITED = "invited"
    SPRINT_COMPLETED = "sprint_completed"
    SYSTEM = "system"
    BILLING = "billing"
    SECURITY = "security"

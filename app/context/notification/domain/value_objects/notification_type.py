from __future__ import annotations

from enum import Enum


class NotificationType(Enum):
    """
    Тип уведомления.

    Новые типы = значение enum.

    Значения:
        TASK_ASSIGNED: Задача назначена
        TASK_UNASSIGNED: Снятие с задачи
        MENTIONED: Пользователь упомянут
        TASK_STATUS_CHANGED: Статус задачи изменён
        TASK_DUE_APPROACHING: Дедлайн задачи приближается
        TASK_OVERDUE: Задача просрочена
        TASK_COMMENT: Новый комментарий к задаче
        TASK_UPDATED: Изменение в задаче (для watchers)
        TASK_DEADLINE_CHANGED: Изменение сроков выполнения задачи
        PROJECT_DEADLINE_APPROACHING: Дедлайн проекта приближается
        PROJECT_OVERDUE: Проект просрочен
        PROJECT_INVITATION: Приглашение в проект
        WORKSPACE_INVITATION: Приглашение в workspace
        ORGANIZATION_INVITATION: Приглашение в организацию
        SPRINT_COMPLETED: Спринт завершён
        SPRINT_STARTED: Спринт начат
        MEETING_SCHEDULED: Встреча запланирована
        MEETING_CANCELLED: Встреча отменена
        MEETING_REMINDER: Напоминание о встрече
        BILLING_PAYMENT_SUCCESS: Успешная оплата
        BILLING_PAYMENT_FAILED: Неудачная оплата
        BILLING_TRIAL_ENDING: Окончание trial
        BILLING_QUOTA_WARNING: Приближение к лимиту
        SECURITY_NEW_DEVICE: Вход с нового устройства
        SECURITY_PASSWORD_CHANGED: Пароль изменён
        SECURITY_2FA_CHANGED: 2FA изменена
        SYSTEM_MAINTENANCE: Плановые работы
        TIME_REMINDER: Напоминание о незаполненном времени
        WELCOME: Приветственное сообщение
    """

    TASK_ASSIGNED = "task_assigned"
    TASK_UNASSIGNED = "task_unassigned"
    MENTIONED = "mentioned"
    TASK_STATUS_CHANGED = "task_status_changed"
    TASK_DUE_APPROACHING = "task_due_approaching"
    TASK_OVERDUE = "task_overdue"
    TASK_COMMENT = "task_comment"
    TASK_UPDATED = "task_updated"
    TASK_DEADLINE_CHANGED = "task_deadline_changed"
    PROJECT_DEADLINE_APPROACHING = "project_deadline_approaching"
    PROJECT_OVERDUE = "project_overdue"
    PROJECT_INVITATION = "project_invitation"
    WORKSPACE_INVITATION = "workspace_invitation"
    ORGANIZATION_INVITATION = "organization_invitation"
    SPRINT_COMPLETED = "sprint_completed"
    SPRINT_STARTED = "sprint_started"
    MEETING_SCHEDULED = "meeting_scheduled"
    MEETING_CANCELLED = "meeting_cancelled"
    MEETING_REMINDER = "meeting_reminder"
    BILLING_PAYMENT_SUCCESS = "billing_payment_success"
    BILLING_PAYMENT_FAILED = "billing_payment_failed"
    BILLING_TRIAL_ENDING = "billing_trial_ending"
    BILLING_QUOTA_WARNING = "billing_quota_warning"
    SECURITY_NEW_DEVICE = "security_new_device"
    SECURITY_PASSWORD_CHANGED = "security_password_changed"
    SECURITY_2FA_CHANGED = "security_2fa_changed"
    SYSTEM_MAINTENANCE = "system_maintenance"
    TIME_REMINDER = "time_reminder"
    WELCOME = "welcome"

from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.context.notification.domain.value_objects.notification_type import NotificationType
from app.context.notification.domain.value_objects.notification_policy import NotificationPolicy
from app.context.notification.application.dto.notification_type_dto import (
    NotificationTypeDTO,
    NotificationTypeListDTO,
)


class GetNotificationTypesQuery(BaseQuery):
    """Запрос списка типов уведомлений."""

    pass


class GetNotificationTypesHandler(BaseQueryHandler[GetNotificationTypesQuery, NotificationTypeListDTO]):
    """
    Обработчик запроса типов уведомлений.

    Возвращает все типы из enum NotificationType с описаниями
    и каналами по умолчанию из NotificationPolicy.default().
    """

    async def handle(self, query: GetNotificationTypesQuery) -> NotificationTypeListDTO:
        policy = NotificationPolicy.default()

        # Маппинг enum-значений → человекочитаемые названия
        labels = {
            NotificationType.TASK_ASSIGNED: "Задача назначена",
            NotificationType.TASK_UNASSIGNED: "Снятие с задачи",
            NotificationType.MENTIONED: "Упоминание",
            NotificationType.TASK_STATUS_CHANGED: "Изменение статуса задачи",
            NotificationType.TASK_DUE_APPROACHING: "Приближение дедлайна задачи",
            NotificationType.TASK_OVERDUE: "Задача просрочена",
            NotificationType.TASK_COMMENT: "Комментарий к задаче",
            NotificationType.TASK_UPDATED: "Обновление задачи",
            NotificationType.TASK_DEADLINE_CHANGED: "Изменение сроков задачи",
            NotificationType.PROJECT_DEADLINE_APPROACHING: "Приближение дедлайна проекта",
            NotificationType.PROJECT_INVITATION: "Приглашение в проект",
            NotificationType.WORKSPACE_INVITATION: "Приглашение в workspace",
            NotificationType.ORGANIZATION_INVITATION: "Приглашение в организацию",
            NotificationType.SPRINT_COMPLETED: "Спринт завершён",
            NotificationType.SPRINT_STARTED: "Спринт начат",
            NotificationType.MEETING_SCHEDULED: "Встреча запланирована",
            NotificationType.MEETING_CANCELLED: "Встреча отменена",
            NotificationType.MEETING_REMINDER: "Напоминание о встрече",
            NotificationType.BILLING_PAYMENT_SUCCESS: "Успешная оплата",
            NotificationType.BILLING_PAYMENT_FAILED: "Неудачная оплата",
            NotificationType.BILLING_TRIAL_ENDING: "Окончание trial-периода",
            NotificationType.BILLING_QUOTA_WARNING: "Приближение к лимиту",
            NotificationType.SECURITY_NEW_DEVICE: "Вход с нового устройства",
            NotificationType.SECURITY_PASSWORD_CHANGED: "Пароль изменён",
            NotificationType.SECURITY_2FA_CHANGED: "2FA изменена",
            NotificationType.SYSTEM_MAINTENANCE: "Плановые работы",
            NotificationType.TIME_REMINDER: "Напоминание о времени",
            NotificationType.WELCOME: "Приветственное сообщение",
        }

        items = []
        for ntype in NotificationType:
            default_channels = policy.default_channels.get(ntype, [])
            items.append(
                NotificationTypeDTO(
                    type=ntype.value,
                    label=labels.get(ntype, ntype.name),
                    default_channels=[ch.value for ch in default_channels],
                )
            )

        return NotificationTypeListDTO(items=items)

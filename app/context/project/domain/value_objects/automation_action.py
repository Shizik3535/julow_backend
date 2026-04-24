from __future__ import annotations

from enum import Enum


class AutomationAction(Enum):
    """
    Действие автоматизации.

    Значения:
        ASSIGN_USER: Назначить пользователя
        CHANGE_STATUS: Изменить статус
        ADD_LABEL: Добавить метку
        SET_DUE_DATE: Установить срок
        SEND_NOTIFICATION: Отправить уведомление
        MOVE_TO_SPRINT: Переместить в спринт
    """

    ASSIGN_USER = "assign_user"
    CHANGE_STATUS = "change_status"
    ADD_LABEL = "add_label"
    SET_DUE_DATE = "set_due_date"
    SEND_NOTIFICATION = "send_notification"
    MOVE_TO_SPRINT = "move_to_sprint"

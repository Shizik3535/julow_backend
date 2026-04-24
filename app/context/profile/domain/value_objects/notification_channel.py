from __future__ import annotations

from enum import Enum


class NotificationChannel(Enum):
    """
    Канал доставки уведомления.

    Значения:
        IN_APP: В приложении.
        EMAIL: По email.
        PUSH: Push-уведомление.
        SMS: SMS-сообщение.
    """

    IN_APP = "in_app"
    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"

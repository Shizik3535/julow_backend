from __future__ import annotations

from enum import Enum


class ChannelType(Enum):
    """
    Канал доставки уведомления.

    Значения:
        IN_APP: В приложении
        EMAIL: Email
        PUSH: Push-уведомление
        WEBHOOK: Webhook
    """

    IN_APP = "in_app"
    EMAIL = "email"
    PUSH = "push"
    WEBHOOK = "webhook"

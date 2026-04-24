from __future__ import annotations

from datetime import datetime

from app.shared.application.base_dto import BaseDTO


class SessionDTO(BaseDTO):
    """
    DTO сессии (Identity BC).

    Атрибуты:
        id: Идентификатор сессии.
        user_id: ID пользователя.
        device_info: User-Agent устройства.
        ip_address: IP-адрес.
        status: Статус сессии.
        is_remember_me: Флаг «Запомнить меня».
        created_at: Время создания.
        expires_at: Время истечения.
    """

    id: str
    user_id: str
    device_info: str
    ip_address: str
    status: str
    is_remember_me: bool
    created_at: datetime
    expires_at: datetime

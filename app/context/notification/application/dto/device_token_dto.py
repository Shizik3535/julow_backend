from __future__ import annotations

from datetime import datetime

from app.shared.application.base_dto import BaseDTO


class DeviceTokenDTO(BaseDTO):
    """
    DTO токена устройства.

    Атрибуты:
        id: Идентификатор.
        platform: Платформа (ios/android/web).
        device_name: Название устройства.
        is_active: Активен ли.
        last_used_at: Время последнего использования.
    """

    id: str = ""
    platform: str = ""
    device_name: str = ""
    is_active: bool = True
    last_used_at: datetime | None = None

from __future__ import annotations

from app.shared.application.base_dto import BaseDTO
from app.context.notification.application.dto.device_token_dto import DeviceTokenDTO


class DeviceTokenListDTO(BaseDTO):
    """
    DTO списка токенов устройств.

    Атрибуты:
        items: Список токенов.
    """

    items: list[DeviceTokenDTO] = []

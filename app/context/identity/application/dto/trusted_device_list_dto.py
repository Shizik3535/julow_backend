from __future__ import annotations

from app.shared.application.base_dto import BaseDTO
from app.context.identity.application.dto.trusted_device_dto import TrustedDeviceDTO


class TrustedDeviceListDTO(BaseDTO):
    """
    DTO списка доверенных устройств (Identity BC).

    Атрибуты:
        items: Список устройств.
        total: Общее количество.
    """

    items: list[TrustedDeviceDTO]
    total: int

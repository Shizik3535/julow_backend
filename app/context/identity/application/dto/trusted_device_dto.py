from __future__ import annotations

from datetime import datetime

from app.shared.application.base_dto import BaseDTO


class TrustedDeviceDTO(BaseDTO):
    """
    DTO доверенного устройства (Identity BC).

    Атрибуты:
        device_fingerprint: Отпечаток устройства.
        user_agent: User-Agent устройства.
        ip: IP-адрес.
        trusted_at: Время добавления в доверенные.
        expires_at: Время истечения доверия.
    """

    device_fingerprint: str
    user_agent: str
    ip: str
    trusted_at: datetime | None = None
    expires_at: datetime | None = None
